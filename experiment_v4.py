import numpy as np
import math
import time
from collections import deque
import pandas as pd

class DFSTimeoutException(Exception):
    pass

# ==========================================
# 1. 基础图与支持超时的 DFS 寻路模块 (修正无环收益归零)
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
        self.best_profit = -1.0
        self.best_path = None
        self.op_count = 0
        start_time = time.perf_counter()

        def dfs(start_node, curr_node, path, curr_rate, visited):
            self.op_count += 1
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
            # 显式修复：如果没有找到任何环（即 best_path 为 None），返回利润 0.0
            if self.best_path is None:
                return None, 0.0, False
            return self.best_path, self.best_profit, False
        except DFSTimeoutException:
            return None, 0.0, True

    def calc_profit(self, path):
        if not path: return 0.0
        product = 1.0
        for i in range(len(path)):
            u = path[i]
            v = path[(i+1)%len(path)]
            for e in self.adj[u]:
                if e.to == v:
                    product *= e.rate 
                    break
        return product - 1.0

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
# 3. 强力最大节点数限制的诱导子图算法
# ==========================================
class PruningAlgorithms:
    @classmethod
    def _extract_hot_induced_subgraph(cls, R, Delta_Matrix, max_nodes):
        N = R.shape[0]
        edges = []
        for i in range(N):
            for j in range(N):
                if i != j:
                    edges.append((i, j, Delta_Matrix[i, j]))
        edges.sort(key=lambda x: x[2], reverse=True)
        
        hot_nodes = set()
        for u, v, val in edges:
            hot_nodes.add(u)
            hot_nodes.add(v)
            if len(hot_nodes) >= max_nodes:
                break
        
        hot_nodes_list = list(hot_nodes)[:max_nodes]
        
        R_pruned = np.zeros_like(R)
        for i in hot_nodes_list:
            for j in hot_nodes_list:
                if i != j:
                    R_pruned[i, j] = R[i, j]
        return R_pruned

    @classmethod
    def laplacian_induced_pruning(cls, R, max_nodes):
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
                
        return cls._extract_hot_induced_subgraph(R, Delta_M, max_nodes)

    @classmethod
    def svd_induced_pruning(cls, R, max_nodes):
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
        
        return cls._extract_hot_induced_subgraph(R, Delta_R, max_nodes)

# ==========================================
# 4. 实验管理与极值理论推导评估
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
        if path is None:
            profit = 0.0
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

    @staticmethod
    def calculate_theoretical_expectation(N, noise_level, L):
        """
        基于极值理论 (EVT) 推导出的噪声背景下 L-步最优简单有向环期望收益
        """
        # E[P_max] = delta * L * sqrt(2/3 * ln N)
        return noise_level * L * math.sqrt((2.0 / 3.0) * math.log(N))

    @classmethod
    def execute_suite(cls):
        num_replicates = 3 
        noise_level = 0.005 # 固定测试中的噪声水平
        
        print("正在进行基准性能校准 (N=10)...")
        R_calib = ExchangeRateGenerator.generate(10, noise_level, True, seed=100)
        _, t_calib, _ = cls.run_dfs_with_timeout(R_calib)
        print(f"校准完成。10阶完全图全局 DFS 均值耗时: {t_calib:.2f} ms\n")

        # ==========================================
        # 实验 A：小规模绝对精度与耗时实验
        # ==========================================
        print("="*80 + "\n实验 A：小规模绝对精度与耗时实验 (重复3次)\n" + "="*80)
        small_results = []
        for N in [8, 10]:
            for trap in [False, True]:
                r_base_p, r_base_t = [], []
                r_lap_p6, r_lap_t6 = [], []  
                r_lap_p8, r_lap_t8 = [], []  
                r_svd_p8, r_svd_t8 = [], []  
                
                for seed in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=seed*10)
                    
                    bp, bt, _ = cls.run_dfs_with_timeout(R)
                    r_base_p.append(bp); r_base_t.append(bt)
                    
                    # Lap 6 Nodes
                    R_l6 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=6)
                    lp6, lt6, _ = cls.run_dfs_with_timeout(R_l6)
                    opt_l6 = (lp6 / bp) * 100 if bp > 0 else (100.0 if lp6 == 0 else 0.0)
                    r_lap_p6.append(opt_l6); r_lap_t6.append(lt6)
                    
                    # Lap 8 Nodes
                    R_l8 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=8)
                    lp8, lt8, _ = cls.run_dfs_with_timeout(R_l8)
                    opt_l8 = (lp8 / bp) * 100 if bp > 0 else (100.0 if lp8 == 0 else 0.0)
                    r_lap_p8.append(opt_l8); r_lap_t8.append(lt8)
                    
                    # SVD 8 Nodes
                    R_s8 = PruningAlgorithms.svd_induced_pruning(R, max_nodes=8)
                    sp8, st8, _ = cls.run_dfs_with_timeout(R_s8)
                    opt_s8 = (sp8 / bp) * 100 if bp > 0 else (100.0 if sp8 == 0 else 0.0)
                    r_svd_p8.append(opt_s8); r_svd_t8.append(st8)
                
                small_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Profit': f"{np.mean(r_base_p)*100:.3f}%±{np.std(r_base_p)*100:.2f}%",
                    'Base Time': f"{np.mean(r_base_t):.1f}±{np.std(r_base_t):.1f} ms",
                    
                    'Lap-6Node Opt': f"{np.mean(r_lap_p6):.1f}%±{np.std(r_lap_p6):.1f}%",
                    'Lap-6Node Time': f"{np.mean(r_lap_t6):.2f}±{np.std(r_lap_t6):.2f} ms",
                    
                    'Lap-8Node Opt': f"{np.mean(r_lap_p8):.1f}%±{np.std(r_lap_p8):.1f}%",
                    'Lap-8Node Time': f"{np.mean(r_lap_t8):.2f}±{np.std(r_lap_t8):.2f} ms",
                    
                    'SVD-8Node Opt': f"{np.mean(r_svd_p8):.1f}%±{np.std(r_svd_p8):.1f}%",
                    'SVD-8Node Time': f"{np.mean(r_svd_t8):.2f}±{np.std(r_svd_t8):.2f} ms"
                })
        print(pd.DataFrame(small_results).to_markdown(index=False))

        # ==========================================
        # 实验 B：大规模硬约束诱导子图实验 (N = 50, 100, 200)
        # ==========================================
        print("\n\n" + "="*80 + "\n实验 B：大规模硬约束诱导子图实验 (控制诱导大小为 6, 8, 10)\n" + "="*80)
        large_results = []
        for N in [50, 100, 200]:
            # 计算无陷阱状态下的极值期望收益 (基于 L=8 评估)
            exp_profit_8 = cls.calculate_theoretical_expectation(N, noise_level, L=8)
            print(f" -> 理论参考: N={N} 时，8-步随机最优简单环理论利润期望值为: {exp_profit_8*100:.3f}%")
            
            for trap in [False, True]:
                t_base_est = cls.format_estimated_time(t_calib, 10, N)
                
                r_lap_p6, r_lap_t6 = [], []
                r_lap_p8, r_lap_t8 = [], []
                r_svd_p8, r_svd_t8 = [], []
                
                lap6_to_count, lap8_to_count, svd8_to_count = 0, 0, 0
                
                for seed in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=seed*20)
                    
                    # Lap 6 Nodes (极大剪枝)
                    R_l6 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=6)
                    lp6, lt6, to_l6 = cls.run_dfs_with_timeout(R_l6, timeout=10.0)
                    if to_l6: lap6_to_count += 1
                    else: r_lap_p6.append(lp6); r_lap_t6.append(lt6)
                    
                    # Lap 8 Nodes (推荐剪枝)
                    R_l8 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=8)
                    lp8, lt8, to_l8 = cls.run_dfs_with_timeout(R_l8, timeout=10.0)
                    if to_l8: lap8_to_count += 1
                    else: r_lap_p8.append(lp8); r_lap_t8.append(lt8)
                    
                    # SVD 8 Nodes
                    R_s8 = PruningAlgorithms.svd_induced_pruning(R, max_nodes=8)
                    sp8, st8, to_s8 = cls.run_dfs_with_timeout(R_s8, timeout=10.0)
                    if to_s8: svd8_to_count += 1
                    else: r_svd_p8.append(sp8); r_svd_t8.append(st8)

                # 计算基准相对利润
                valid_profits = []
                if r_lap_p6: valid_profits.append(np.mean(r_lap_p6))
                if r_lap_p8: valid_profits.append(np.mean(r_lap_p8))
                if r_svd_p8: valid_profits.append(np.mean(r_svd_p8))
                max_profit_mean = max(valid_profits) if valid_profits else 0.0
                
                def fmt_metric(p_list, t_list, to_count):
                    if to_count == num_replicates:
                        return "Timeout", "Timeout"
                    opt = (np.mean(p_list) / max_profit_mean * 100) if max_profit_mean > 0 else 0.0
                    p_str = f"{opt:.1f}%" + (f" ({to_count}TO)" if to_count > 0 else "")
                    t_str = f"{np.mean(t_list):.1f}±{np.std(t_list):.1f} ms"
                    return p_str, t_str

                l6_p_str, l6_t_str = fmt_metric(r_lap_p6, r_lap_t6, lap6_to_count)
                l8_p_str, l8_t_str = fmt_metric(r_lap_p8, r_lap_t8, lap8_to_count)
                s8_p_str, s8_t_str = fmt_metric(r_svd_p8, r_svd_t8, svd8_to_count)

                large_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Est Time': t_base_est,
                    'Lap-6Node Opt': l6_p_str, 'Lap-6Node Time': l6_t_str,
                    'Lap-8Node Opt': l8_p_str, 'Lap-8Node Time': l8_t_str,
                    'SVD-8Node Opt': s8_p_str, 'SVD-8Node Time': s8_t_str
                })
        print(pd.DataFrame(large_results).to_markdown(index=False))

if __name__ == "__main__":
    ExperimentRunner.execute_suite()