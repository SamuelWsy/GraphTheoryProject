import numpy as np
import math
import time
from collections import deque
import pandas as pd

class DFSTimeoutException(Exception):
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
# 3. 强力最大节点数限制的无错诱导子图剪枝算法
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
# 4. 实验控制中心 (统一大/小规模表格、增加5次独立重构)
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
        基于极值理论 (EVT) 推导出的噪声背景下 L-步最优简单有向环期望收益公式
        E[P] = delta * L * sqrt(2/3 * ln N)
        """
        if N < L: return 0.0
        return noise_level * L * math.sqrt((2.0 / 3.0) * math.log(N))

    @classmethod
    def format_cell(cls, p_list, t_list, to_count, base_p_mean=None, is_large=False, max_empirical_p=None):
        if to_count == len(p_list) and is_large:
            return "Timeout"
        
        p_mean = np.mean(p_list) * 100
        p_std = np.std(p_list) * 100
        t_mean = np.mean(t_list)
        t_std = np.std(t_list)
        
        # 计算 Optimality
        if not is_large:
            opt = (p_mean / (base_p_mean * 100)) * 100 if base_p_mean > 0 else (100.0 if p_mean == 0 else 0.0)
        else:
            opt = (p_mean / (max_empirical_p * 100)) * 100 if max_empirical_p > 0 else 0.0
            
        to_str = f" ({to_count}TO)" if to_count > 0 else ""
        return f"{p_mean:.3f}%±{p_std:.2f}% ({opt:.1f}%){to_str} / {t_mean:.2f}±{t_std:.2f} ms"

    @classmethod
    def execute_suite(cls):
        num_replicates = 5 # 设定每个参数组合重复进行 5 次独立重构实验
        noise_level = 0.005 
        
        print("正在进行基准性能校准 (N=10)...")
        R_calib = ExchangeRateGenerator.generate(10, noise_level, True, seed=100)
        _, t_calib, _ = cls.run_dfs_with_timeout(R_calib)
        print(f"校准完成。10阶完全图全局 DFS 均值耗时: {t_calib:.2f} ms\n")

        # ==========================================
        # 实验 A：小规模绝对精度与耗时实验
        # ==========================================
        print("="*120 + "\n实验 A：小规模绝对精度与耗时实验 (重复5次，数据完全重新生成)\n" + "="*120)
        small_results = []
        for N in [8, 10]:
            # 计算小规模下的概率论理论值 (t)
            e6 = cls.calculate_theoretical_expectation(N, noise_level, L=6)
            e8 = cls.calculate_theoretical_expectation(N, noise_level, L=8)
            e6_str = f"{e6*100:.3f}% (t)" if e6 > 0 else "N/A"
            e8_str = f"{e8*100:.3f}% (t)" if e8 > 0 else "N/A"
            
            for trap in [False, True]:
                r_base_p, r_base_t = [], []
                r_lap_p6, r_lap_t6 = [], []  
                r_lap_p8, r_lap_t8 = [], []  
                r_svd_p8, r_svd_t8 = [], []  
                
                for _ in range(num_replicates):
                    # seed=None 保证每一次都是全新独立重构的汇率矩阵
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=None)
                    
                    bp, bt, _ = cls.run_dfs_with_timeout(R)
                    r_base_p.append(bp); r_base_t.append(bt)
                    
                    # Lap 6 Nodes
                    R_l6 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=6)
                    lp6, lt6, _ = cls.run_dfs_with_timeout(R_l6)
                    r_lap_p6.append(lp6); r_lap_t6.append(lt6)
                    
                    # Lap 8 Nodes
                    R_l8 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=8)
                    lp8, lt8, _ = cls.run_dfs_with_timeout(R_l8)
                    r_lap_p8.append(lp8); r_lap_t8.append(lt8)
                    
                    # SVD 8 Nodes
                    R_s8 = PruningAlgorithms.svd_induced_pruning(R, max_nodes=8)
                    sp8, st8, _ = cls.run_dfs_with_timeout(R_s8)
                    r_svd_p8.append(sp8); r_svd_t8.append(st8)
                
                bp_mean = np.mean(r_base_p)
                bp_std = np.std(r_base_p)
                bt_mean = np.mean(r_base_t)
                bt_std = np.std(r_base_t)
                
                small_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Prof/Time': f"{bp_mean*100:.3f}%±{bp_std*100:.2f}% / {bt_mean:.2f}±{bt_std:.2f} ms",
                    'L=6 (t)': e6_str,
                    'Lap-6Node Prof(Opt)/Time': cls.format_cell(r_lap_p6, r_lap_t6, 0, bp_mean, False),
                    'L=8 (t)': e8_str,
                    'Lap-8Node Prof(Opt)/Time': cls.format_cell(r_lap_p8, r_lap_t8, 0, bp_mean, False),
                    'SVD-8Node Prof(Opt)/Time': cls.format_cell(r_svd_p8, r_svd_t8, 0, bp_mean, False)
                })
        print(pd.DataFrame(small_results).to_markdown(index=False))

        # ==========================================
        # 实验 B：大规模硬约束诱导子图实验 (控制诱导大小为 6, 8, 10)
        # ==========================================
        print("\n\n" + "="*120 + "\n实验 B：大规模硬约束诱导子图实验 (重复5次，数据完全重新生成)\n" + "="*120)
        large_results = []
        for N in [50, 100, 200]:
            # 计算大规模下的概率论理论值 (t)
            e6 = cls.calculate_theoretical_expectation(N, noise_level, L=6)
            e8 = cls.calculate_theoretical_expectation(N, noise_level, L=8)
            e6_str = f"{e6*100:.3f}% (t)" if e6 > 0 else "N/A"
            e8_str = f"{e8*100:.3f}% (t)" if e8 > 0 else "N/A"
            
            for trap in [False, True]:
                t_base_est = cls.format_estimated_time(t_calib, 10, N)
                
                r_lap_p6, r_lap_t6 = [], []
                r_lap_p8, r_lap_t8 = [], []
                r_svd_p8, r_svd_t8 = [], []
                
                lap6_to_count, lap8_to_count, svd8_to_count = 0, 0, 0
                
                for _ in range(num_replicates):
                    # seed=None 保证每一次都是全新独立重构的汇率矩阵
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=None)
                    
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

                # 寻找最大经验利润
                valid_profits = []
                if r_lap_p6: valid_profits.append(np.mean(r_lap_p6))
                if r_lap_p8: valid_profits.append(np.mean(r_lap_p8))
                if r_svd_p8: valid_profits.append(np.mean(r_svd_p8))
                max_profit_mean = max(valid_profits) if valid_profits else 0.0

                large_results.append({
                    'N': N, 'Trap': str(trap),
                    'Base Prof/Time': f"-- / Est: {t_base_est}",
                    'L=6 (t)': e6_str,
                    'Lap-6Node Prof(Opt)/Time': cls.format_cell(r_lap_p6, r_lap_t6, lap6_to_count, is_large=True, max_empirical_p=max_profit_mean),
                    'L=8 (t)': e8_str,
                    'Lap-8Node Prof(Opt)/Time': cls.format_cell(r_lap_p8, r_lap_t8, lap8_to_count, is_large=True, max_empirical_p=max_profit_mean),
                    'SVD-8Node Prof(Opt)/Time': cls.format_cell(r_svd_p8, r_svd_t8, svd8_to_count, is_large=True, max_empirical_p=max_profit_mean)
                })
        print(pd.DataFrame(large_results).to_markdown(index=False))

if __name__ == "__main__":
    ExperimentRunner.execute_suite()