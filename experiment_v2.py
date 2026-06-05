import numpy as np
import math
import time
from collections import deque
import pandas as pd

class DFSTimeoutException(Exception):
    """自定义的超时异常"""
    pass

# ==========================================
# 1. 基础图与支持超时的 DFS 寻路模块
# ==========================================
class Edge:
    def __init__(self, to, rate):
        self.to = to
        self.rate = rate

class OptimalArbitrageDFS:
    def __init__(self, n):
        self.N = n
        self.adj = [[] for _ in range(n)]
        self.best_profit = -1.0
        self.best_path = None
        self.op_count = 0

    def add_edge(self, fr, to, rate):
        if rate <= 0: return
        self.adj[fr].append(Edge(to, rate))

    def find_optimal_arbitrage(self, timeout=10.0):
        """
        寻找全局最优简单回路，支持 10 秒硬超时打断
        """
        self.best_profit = -1.0
        self.best_path = None
        self.op_count = 0
        start_time = time.perf_counter()

        def dfs(start_node, curr_node, path, curr_rate, visited):
            self.op_count += 1
            # 每 5000 次递归进行一次时间检查，减小 CPU 开销
            if self.op_count % 5000 == 0:
                if time.perf_counter() - start_time > timeout:
                    raise DFSTimeoutException()

            for e in self.adj[curr_node]:
                if e.to == start_node:
                    profit = curr_rate * e.rate - 1.0
                    if profit > self.best_profit:
                        self.best_profit = profit
                        self.best_path = path.copy()
                elif e.to not in visited and e.to > start_node:
                    visited.add(e.to)
                    path.append(e.to)
                    dfs(start_node, e.to, path, curr_rate * e.rate, visited)
                    path.pop()
                    visited.remove(e.to)

        try:
            for i in range(self.N):
                dfs(i, i, [i], 1.0, {i})
            return self.best_path, self.best_profit, False
        except DFSTimeoutException:
            return None, -1.0, True

# ==========================================
# 2. 汇率矩阵生成器
# ==========================================
class ExchangeRateGenerator:
    @staticmethod
    def generate(N, noise_level, inject_trap, seed=None):
        if seed is not None:
            np.random.seed(seed)
        prices = np.random.uniform(0.5, 5.0, N)
        R = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    ideal_rate = prices[j] / prices[i]
                    noise = np.random.uniform(-noise_level, noise_level)
                    R[i, j] = ideal_rate * (1 + noise)
        if inject_trap and N >= 4:
            R[0, 1] = (prices[1]/prices[0]) * 1.04
            R[1, 2] = (prices[2]/prices[1]) * 1.04
            R[2, 3] = (prices[3]/prices[2]) * 1.04
            R[3, 0] = (prices[0]/prices[3]) * 0.98
        return R

# ==========================================
# 3. 严格控制稀疏度的剪枝算法 (Direct Sparsification)
# ==========================================
class PruningAlgorithms:
    @staticmethod
    def laplacian_pruning(R, retain_ratio):
        """
        图拉普拉斯剪枝：严格只保留前 K 个最大残差边，确保图的绝对稀疏性
        """
        N = R.shape[0]
        M = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j and R[i, j] > 0: M[i, j] = math.log(R[i, j])
        
        y = np.mean(M, axis=0)
        Delta_M = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j: Delta_M[i, j] = M[i, j] - (y[j] - y[i])
        
        # 严格获取前 K 个最大边
        flat_delta = Delta_M.flatten()
        K = int(N * N * retain_ratio)
        if K == 0: K = 1
        threshold = np.sort(flat_delta)[-K]
        
        R_pruned = np.zeros_like(R)
        for i in range(N):
            for j in range(N):
                if i != j and Delta_M[i, j] >= threshold:
                    R_pruned[i, j] = R[i, j]
        return R_pruned

    @staticmethod
    def svd_sinkhorn_pruning(R, retain_ratio):
        """
        SVD 剪枝：严格保留前 K 个最大残差边
        """
        N = R.shape[0]
        R_bal = R.copy()
        for _ in range(5):
            r_sum = R_bal.sum(axis=1, keepdims=True)
            R_bal = np.divide(R_bal, r_sum, where=r_sum!=0)
            c_sum = R_bal.sum(axis=0, keepdims=True)
            R_bal = np.divide(R_bal, c_sum, where=c_sum!=0)
            
        U, S, Vh = np.linalg.svd(R_bal)
        R_hat = S[0] * np.outer(U[:, 0], Vh[0, :])
        Delta_R = R_bal - R_hat
        
        K = int(N * N * retain_ratio)
        top_k_indices = np.argsort(Delta_R.flatten())[::-1][:K]
        
        R_pruned = np.zeros_like(R)
        for idx in top_k_indices:
            i, j = divmod(idx, N)
            if i != j: R_pruned[i, j] = R[i, j]
        return R_pruned

# ==========================================
# 4. 实验管理与外推估算模块
# ==========================================
class ExperimentRunner:
    @staticmethod
    def run_dfs_with_timeout(R, timeout=10.0):
        N = R.shape[0]
        solver = OptimalArbitrageDFS(N)
        for i in range(N):
            for j in range(N):
                if R[i, j] > 0: solver.add_edge(i, j, R[i, j])
        start = time.perf_counter()
        path, profit, timeout_triggered = solver.find_optimal_arbitrage(timeout)
        elapsed = (time.perf_counter() - start) * 1000
        return profit, elapsed, timeout_triggered

    @staticmethod
    def format_estimated_time(t_0, N_0, N_target):
        try:
            ratio = math.factorial(N_target) / math.factorial(N_0)
            t_est_ms = t_0 * ratio
            t_est_years = t_est_ms / (1000 * 3600 * 24 * 365)
            if t_est_years < 1.0:
                return f"{t_est_ms/1000:.2f} s" if t_est_ms > 1000 else f"{t_est_ms:.1f} ms"
            elif t_est_years < 1e6:
                return f"{t_est_years:.1f} 年"
            else:
                exponent = int(math.log10(t_est_years))
                return f"约 10^{exponent} 年"
        except OverflowError:
            return "接近无限时间"

    @classmethod
    def execute_suite(cls):
        num_replicates = 3 # 设定每个参数组合重复进行 3 次实验获取均值和标准差
        
        # 校准时间常数
        print("正在进行基准性能校准 (N=10)...")
        R_calib = ExchangeRateGenerator.generate(10, 0.005, True, seed=100)
        _, t_calib, _ = cls.run_dfs_with_timeout(R_calib)
        print(f"校准完成。10阶完全图全局 DFS 均值耗时: {t_calib:.2f} ms\n")

        # ==========================================
        # 实验 A：小规模绝对精度与稳定性实验 (N <= 10)
        # ==========================================
        print("="*80 + "\n实验 A：小规模绝对精度实验 (对数百分比度量，重复3次)\n" + "="*80)
        small_results = []
        for N in [8, 10]:
            for trap in [False, True]:
                # 记录 3 次重复实验的数据
                r_base_p, r_base_t = [], []
                r_lap_p2, r_lap_t2 = [], []  # Lap 强度 2%
                r_lap_p5, r_lap_t5 = [], []  # Lap 强度 5%
                r_svd_p5, r_svd_t5 = [], []  # SVD 强度 5%
                
                for seed in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, 0.005, trap, seed=seed*10)
                    
                    # Base
                    bp, bt, _ = cls.run_dfs_with_timeout(R)
                    r_base_p.append(bp); r_base_t.append(bt)
                    
                    # Lap 2%
                    R_l2 = PruningAlgorithms.laplacian_pruning(R, retain_ratio=0.02)
                    lp2, lt2, _ = cls.run_dfs_with_timeout(R_l2)
                    opt_l2 = (lp2 / bp) if bp > 0 else (1.0 if lp2 == 0 else 0.0)
                    r_lap_p2.append(opt_l2); r_lap_t2.append(lt2)
                    
                    # Lap 5%
                    R_l5 = PruningAlgorithms.laplacian_pruning(R, retain_ratio=0.05)
                    lp5, lt5, _ = cls.run_dfs_with_timeout(R_l5)
                    opt_l5 = (lp5 / bp) if bp > 0 else (1.0 if lp5 == 0 else 0.0)
                    r_lap_p5.append(opt_l5); r_lap_t5.append(lt5)
                    
                    # SVD 5%
                    R_s5 = PruningAlgorithms.svd_sinkhorn_pruning(R, retain_ratio=0.05)
                    sp5, st5, _ = cls.run_dfs_with_timeout(R_s5)
                    opt_s5 = (sp5 / bp) if bp > 0 else (1.0 if sp5 == 0 else 0.0)
                    r_svd_p5.append(opt_s5); r_svd_t5.append(st5)
                
                small_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Profit': f"{np.mean(r_base_p)*100:.3f}%±{np.std(r_base_p)*100:.2f}%",
                    'Base Time': f"{np.mean(r_base_t):.1f}±{np.std(r_base_t):.1f} ms",
                    'Lap-2% Opt': f"{np.mean(r_lap_p2)*100:.1f}%±{np.std(r_lap_p2)*100:.1f}%",
                    'Lap-5% Opt': f"{np.mean(r_lap_p5)*100:.1f}%±{np.std(r_lap_p5)*100:.1f}%",
                    'SVD-5% Opt': f"{np.mean(r_svd_p5)*100:.1f}%±{np.std(r_svd_p5)*100:.1f}%"
                })
        print(pd.DataFrame(small_results).to_markdown(index=False))

        # ==========================================
        # 实验 B：大规模降维加速与硬超时实验 (N = 50, 100, 200)
        # ==========================================
        print("\n\n" + "="*80 + "\n实验 B：大规模降维加速与硬超时实验 (重复3次)\n" + "="*80)
        large_results = []
        for N in [50, 100, 200]:
            for trap in [False, True]:
                # 理论外推耗时估算
                t_base_est = cls.format_estimated_time(t_calib, 10, N)
                
                r_lap_p2, r_lap_t2 = [], []
                r_lap_p5, r_lap_t5 = [], []
                r_svd_p5, r_svd_t5 = [], []
                
                # 标记超时状态
                lap2_to_count, lap5_to_count, svd5_to_count = 0, 0, 0
                
                for seed in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, 0.005, trap, seed=seed*20)
                    
                    # Lap 2%
                    R_l2 = PruningAlgorithms.laplacian_pruning(R, retain_ratio=0.02)
                    lp2, lt2, to_l2 = cls.run_dfs_with_timeout(R_l2, timeout=10.0)
                    if to_l2: lap2_to_count += 1
                    else: r_lap_p2.append(lp2); r_lap_t2.append(lt2)
                    
                    # Lap 5%
                    R_l5 = PruningAlgorithms.laplacian_pruning(R, retain_ratio=0.05)
                    lp5, lt5, to_l5 = cls.run_dfs_with_timeout(R_l5, timeout=10.0)
                    if to_l5: lap5_to_count += 1
                    else: r_lap_p5.append(lp5); r_lap_t5.append(lt5)
                    
                    # SVD 5%
                    R_s5 = PruningAlgorithms.svd_sinkhorn_pruning(R, retain_ratio=0.05)
                    sp5, st5, to_s5 = cls.run_dfs_with_timeout(R_s5, timeout=10.0)
                    if to_s5: svd5_to_count += 1
                    else: r_svd_p5.append(sp5); r_svd_t5.append(st5)

                # 相对最优性基准（取三者求得的最大绝对利润的均值）
                # 为了安全处理超时：如果全部超时，基准记为0
                valid_profits = []
                if r_lap_p2: valid_profits.append(np.mean(r_lap_p2))
                if r_lap_p5: valid_profits.append(np.mean(r_lap_p5))
                if r_svd_p5: valid_profits.append(np.mean(r_svd_p5))
                max_profit_mean = max(valid_profits) if valid_profits else 0.0
                
                # 格式化输出函数
                def fmt_metric(p_list, t_list, to_count):
                    if to_count == num_replicates:
                        return "Timeout", "Timeout"
                    opt = (np.mean(p_list) / max_profit_mean * 100) if max_profit_mean > 0 else 100.0
                    p_str = f"{opt:.1f}%" + (f" ({to_count}TO)" if to_count > 0 else "")
                    t_str = f"{np.mean(t_list):.1f}±{np.std(t_list):.1f} ms"
                    return p_str, t_str

                l2_p_str, l2_t_str = fmt_metric(r_lap_p2, r_lap_t2, lap2_to_count)
                l5_p_str, l5_t_str = fmt_metric(r_lap_p5, r_lap_t5, lap5_to_count)
                s5_p_str, s5_t_str = fmt_metric(r_svd_p5, r_svd_t5, svd5_to_count)

                large_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Est Time': t_base_est,
                    'Lap-2% Opt': l2_p_str, 'Lap-2% Time': l2_t_str,
                    'Lap-5% Opt': l5_p_str, 'Lap-5% Time': l5_t_str,
                    'SVD-5% Opt': s5_p_str, 'SVD-5% Time': s5_t_str
                })
        print(pd.DataFrame(large_results).to_markdown(index=False))

if __name__ == "__main__":
    ExperimentRunner.execute_suite()