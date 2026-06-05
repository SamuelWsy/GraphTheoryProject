import numpy as np
import math
import time
import itertools
from collections import deque, defaultdict
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
        if rate <= 0:
            return
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
        if not path:
            return 0.0
        product = 1.0
        for i in range(len(path)):
            u = path[i]
            v = path[(i + 1) % len(path)]
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
            R[0, 1] = (prices[1] / prices[0]) * 1.04
            R[1, 2] = (prices[2] / prices[1]) * 1.04
            R[2, 3] = (prices[3] / prices[2]) * 1.04
            R[3, 0] = (prices[0] / prices[3]) * 0.98

        return R

# ==========================================
# 3. Trapped Expectation 理论估计器
# ==========================================
class TrappedExpectationEstimator:
    """
    估计：E[BestProfit] ≈ exp(max_C S(C)) - 1，其中 S(C)=sum log(q_e)。

    核心改进：
    1. 普通边：q_e = 1 + eps, eps ~ U(-delta, delta)。
    2. trap 边：固定为 r_plus 或 r_minus。
    3. 按“回路长度 l + 包含的 trap 边集合 J”分类，计算每类最大对数收益的极值近似。

    对应近似公式：
    Z_max ≈ max_{l,J} [sum_{e in J} log r_e + (l-|J|)mu
                       + sqrt(l-|J|)sigma sqrt(2 log M_{l,J})]
    E[P_max] ≈ exp(Z_max) - 1
    """

    def __init__(self, noise_level, r_plus=1.04, r_minus=0.98):
        self.noise_level = noise_level
        self.r_plus = r_plus
        self.r_minus = r_minus
        self.trap_rates = {
            (0, 1): r_plus,
            (1, 2): r_plus,
            (2, 3): r_plus,
            (3, 0): r_minus,
        }
        self.trap_edges = tuple(self.trap_rates.keys())
        self.mu_delta, self.sigma_delta = self._log_noise_moments(noise_level)

    @staticmethod
    def _log_noise_moments(delta):
        """X=log(1+eps), eps~U(-delta,delta) 的精确均值与方差。"""
        if delta <= 0:
            return 0.0, 0.0
        if delta >= 1:
            raise ValueError("noise_level must be smaller than 1 so that log(1+eps) is defined.")

        a = 1.0 - delta
        b = 1.0 + delta

        # ∫ log y dy = y log y - y
        ex = ((b * math.log(b) - b) - (a * math.log(a) - a)) / (2.0 * delta)

        # ∫ (log y)^2 dy = y[(log y)^2 - 2log y + 2]
        def F(y):
            ly = math.log(y)
            return y * (ly * ly - 2.0 * ly + 2.0)

        ex2 = (F(b) - F(a)) / (2.0 * delta)
        var = max(0.0, ex2 - ex * ex)
        return ex, math.sqrt(var)

    @staticmethod
    def _comb(n, k):
        if k < 0 or k > n:
            return 0
        return math.comb(n, k)

    @staticmethod
    def _is_closed_directed_cycle(edges):
        if not edges:
            return False
        out_deg = defaultdict(int)
        in_deg = defaultdict(int)
        nodes = set()
        nxt = {}
        for u, v in edges:
            out_deg[u] += 1
            in_deg[v] += 1
            nodes.add(u)
            nodes.add(v)
            nxt[u] = v
        for x in nodes:
            if out_deg[x] != 1 or in_deg[x] != 1:
                return False

        start = next(iter(nodes))
        cur = start
        seen = set()
        for _ in range(len(nodes)):
            if cur in seen or cur not in nxt:
                return False
            seen.add(cur)
            cur = nxt[cur]
        return cur == start and len(seen) == len(nodes)

    @staticmethod
    def _path_component_count(edges):
        """把已指定的 trap 边压缩成若干有向路径块，返回涉及节点数 v 和路径块数 c。"""
        if not edges:
            return 0, 0

        nodes = set()
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        out_deg = defaultdict(int)
        in_deg = defaultdict(int)
        for u, v in edges:
            nodes.add(u)
            nodes.add(v)
            out_deg[u] += 1
            in_deg[v] += 1
            union(u, v)

        # 若某节点出现两个指定出边或两个指定入边，则不可能嵌入简单有向环。
        for x in nodes:
            if out_deg[x] > 1 or in_deg[x] > 1:
                return None, None

        roots = {find(x) for x in nodes}
        return len(nodes), len(roots)

    def _count_cycles_containing_at_least(self, N, L, edge_subset):
        """
        计算长度为 L 的简单有向回路中，至少包含 edge_subset 的数量。
        对本实验的 trap 边集合而言，该计数是精确的。
        """
        edges = tuple(edge_subset)
        k = len(edges)

        if L < 2 or L > N:
            return 0

        if k == 0:
            # 完全有向图中长度为 L 的简单有向环数量：C(N,L)*(L-1)! = (N)_L / L
            return self._comb(N, L) * math.factorial(L - 1)

        if self._is_closed_directed_cycle(edges):
            v = len({x for e in edges for x in e})
            return 1 if L == v else 0

        v, c = self._path_component_count(edges)
        if v is None:
            return 0

        s = L - v
        if s < 0:
            return 0

        # 将每个指定路径块视为一个整体，再加入 s 个普通节点。
        # 总 item 数为 c+s，其有向环排列数为 (c+s-1)!。
        return self._comb(N - v, s) * math.factorial(c + s - 1)

    def _count_cycles_containing_exactly(self, N, L, exact_subset, all_trap_edges):
        """用包含-排除计算：恰好包含 exact_subset，而不包含其他 trap 边。"""
        exact_subset = set(exact_subset)
        remaining = [e for e in all_trap_edges if e not in exact_subset]
        total = 0

        for r in range(len(remaining) + 1):
            for extra in itertools.combinations(remaining, r):
                superset = tuple(sorted(exact_subset.union(extra)))
                sign = -1 if (r % 2 == 1) else 1
                total += sign * self._count_cycles_containing_at_least(N, L, superset)

        # 理论上为整数；浮点/组合抵消后做保护。
        return max(0, int(round(total)))

    def _all_subsets(self, items):
        items = list(items)
        for r in range(len(items) + 1):
            for subset in itertools.combinations(items, r):
                yield tuple(subset)

    def estimate_log_best(self, N, max_cycle_len, inject_trap):
        """
        返回近似的最优对数收益 Z_max，以及给出该最大值的分类信息。
        max_cycle_len 表示诱导子图最大节点数，因此搜索 2..max_cycle_len 的所有简单环。
        """
        max_cycle_len = min(max_cycle_len, N)

        active_trap_edges = self.trap_edges if (inject_trap and N >= 4) else tuple()
        best_z = -float("inf")
        best_info = None

        for L in range(2, max_cycle_len + 1):
            for J in self._all_subsets(active_trap_edges):
                M = self._count_cycles_containing_exactly(N, L, J, active_trap_edges)
                if M <= 0:
                    continue

                trap_log_sum = sum(math.log(self.trap_rates[e]) for e in J)
                random_edge_count = L - len(J)

                mean = trap_log_sum + random_edge_count * self.mu_delta
                std = math.sqrt(random_edge_count) * self.sigma_delta

                extreme_bonus = 0.0 if M <= 1 or std == 0 else std * math.sqrt(2.0 * math.log(M))
                z = mean + extreme_bonus

                if z > best_z:
                    best_z = z
                    best_info = {
                        "cycle_len": L,
                        "trap_edges": J,
                        "candidate_count": M,
                        "random_edge_count": random_edge_count,
                        "mean_log": mean,
                        "std_log": std,
                        "extreme_bonus": extreme_bonus,
                    }

        if best_z == -float("inf"):
            return 0.0, None
        return best_z, best_info

    def estimate_profit(self, N, max_cycle_len, inject_trap):
        z, info = self.estimate_log_best(N, max_cycle_len, inject_trap)
        return math.exp(z) - 1.0, info

    def format_estimate(self, N, max_cycle_len, inject_trap):
        profit, info = self.estimate_profit(N, max_cycle_len, inject_trap)
        if info is None:
            return "N/A"
        return f"{profit * 100:.3f}% (t)"

# ==========================================
# 4. 强力最大节点数限制的无错诱导子图剪枝算法
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
                if i != j and R[i, j] > 0:
                    M[i, j] = math.log(R[i, j])

        y = np.mean(M, axis=0)
        Delta_M = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    Delta_M[i, j] = M[i, j] - (y[j] - y[i])

        return cls._extract_hot_induced_subgraph(R, Delta_M, max_nodes)

    @classmethod
    def svd_induced_pruning(cls, R, max_nodes):
        N = R.shape[0]
        R_bal = R.copy()
        for _ in range(5):
            r_sum = R_bal.sum(axis=1, keepdims=True)
            R_bal = np.divide(R_bal, r_sum, where=r_sum != 0)
            c_sum = R_bal.sum(axis=0, keepdims=True)
            R_bal = np.divide(R_bal, c_sum, where=c_sum != 0)

        U, S, Vh = np.linalg.svd(R_bal)
        R_hat = S[0] * np.outer(U[:, 0], Vh[0, :])
        Delta_R = R_bal - R_hat

        return cls._extract_hot_induced_subgraph(R, Delta_R, max_nodes)

# ==========================================
# 5. 实验控制中心
# ==========================================
class ExperimentRunner:
    @staticmethod
    def run_dfs_with_timeout(R, timeout=10.0):
        N = R.shape[0]
        solver = OptimalArbitrageDFS(N)
        for i in range(N):
            for j in range(N):
                if R[i, j] > 0:
                    solver.add_edge(i, j, R[i, j])
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
                return f"{t_est_ms / 1000:.2f} s" if t_est_ms > 1000 else f"{t_est_ms:.1f} ms"
            elif t_est_years < 1e6:
                return f"{t_est_years:.1f} 年"
            else:
                exponent = int(math.log10(t_est_years))
                return f"约 10^{exponent} 年"
        except OverflowError:
            return "接近无限时间"

    @classmethod
    def format_cell(cls, p_list, t_list, to_count, base_p_mean=None, is_large=False, max_empirical_p=None):
        if len(p_list) == 0:
            return "Timeout" if to_count > 0 else "N/A"
        if to_count == len(p_list) and is_large:
            return "Timeout"

        p_mean = np.mean(p_list) * 100
        p_std = np.std(p_list) * 100
        t_mean = np.mean(t_list)
        t_std = np.std(t_list)

        if not is_large:
            opt = (p_mean / (base_p_mean * 100)) * 100 if base_p_mean > 0 else (100.0 if p_mean == 0 else 0.0)
        else:
            opt = (p_mean / (max_empirical_p * 100)) * 100 if max_empirical_p > 0 else 0.0

        to_str = f" ({to_count}TO)" if to_count > 0 else ""
        return f"{p_mean:.3f}%±{p_std:.2f}% ({opt:.1f}%){to_str} / {t_mean:.2f}±{t_std:.2f} ms"

    @classmethod
    def execute_suite(cls):
        num_replicates = 5
        noise_level = 0.005
        estimator = TrappedExpectationEstimator(noise_level=noise_level, r_plus=1.04, r_minus=0.98)

        print("正在进行基准性能校准 (N=10)...")
        R_calib = ExchangeRateGenerator.generate(10, noise_level, True, seed=100)
        _, t_calib, _ = cls.run_dfs_with_timeout(R_calib)
        print(f"校准完成。10阶完全图全局 DFS 均值耗时: {t_calib:.2f} ms\n")

        print("理论模型说明：")
        print("  普通边: q=1+eps, eps~U(-delta,delta)")
        print("  trap边: 0->1,1->2,2->3 乘 1.04；3->0 乘 0.98")
        print("  理论列 E≤L(t) 表示在最大环长不超过 L 的简单有向环中，trapped expectation 的极值近似。\n")

        # ==========================================
        # 实验 A：小规模绝对精度与耗时实验
        # ==========================================
        print("=" * 120 + "\n实验 A：小规模绝对精度与耗时实验 (重复5次，数据完全重新生成)\n" + "=" * 120)
        small_results = []
        for N in [8, 10]:
            for trap in [False, True]:
                e6_str = estimator.format_estimate(N, max_cycle_len=6, inject_trap=trap)
                e8_str = estimator.format_estimate(N, max_cycle_len=8, inject_trap=trap)

                r_base_p, r_base_t = [], []
                r_lap_p6, r_lap_t6 = [], []
                r_lap_p8, r_lap_t8 = [], []
                r_svd_p8, r_svd_t8 = [], []

                for _ in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=None)

                    bp, bt, _ = cls.run_dfs_with_timeout(R)
                    r_base_p.append(bp)
                    r_base_t.append(bt)

                    R_l6 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=6)
                    lp6, lt6, _ = cls.run_dfs_with_timeout(R_l6)
                    r_lap_p6.append(lp6)
                    r_lap_t6.append(lt6)

                    R_l8 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=8)
                    lp8, lt8, _ = cls.run_dfs_with_timeout(R_l8)
                    r_lap_p8.append(lp8)
                    r_lap_t8.append(lt8)

                    R_s8 = PruningAlgorithms.svd_induced_pruning(R, max_nodes=8)
                    sp8, st8, _ = cls.run_dfs_with_timeout(R_s8)
                    r_svd_p8.append(sp8)
                    r_svd_t8.append(st8)

                bp_mean = np.mean(r_base_p)
                bp_std = np.std(r_base_p)
                bt_mean = np.mean(r_base_t)
                bt_std = np.std(r_base_t)

                small_results.append({
                    "N": N,
                    "Trap": str(trap),
                    "Base Prof/Time": f"{bp_mean * 100:.3f}%±{bp_std * 100:.2f}% / {bt_mean:.2f}±{bt_std:.2f} ms",
                    "E≤6 (t)": e6_str,
                    "Lap-6Node Prof(Opt)/Time": cls.format_cell(r_lap_p6, r_lap_t6, 0, bp_mean, False),
                    "E≤8 (t)": e8_str,
                    "Lap-8Node Prof(Opt)/Time": cls.format_cell(r_lap_p8, r_lap_t8, 0, bp_mean, False),
                    "SVD-8Node Prof(Opt)/Time": cls.format_cell(r_svd_p8, r_svd_t8, 0, bp_mean, False),
                })
        print(pd.DataFrame(small_results).to_markdown(index=False))

        # ==========================================
        # 实验 B：大规模硬约束诱导子图实验
        # ==========================================
        print("\n\n" + "=" * 120 + "\n实验 B：大规模硬约束诱导子图实验 (重复5次，数据完全重新生成)\n" + "=" * 120)
        large_results = []
        for N in [50, 100, 200]:
            for trap in [False, True]:
                e6_str = estimator.format_estimate(N, max_cycle_len=6, inject_trap=trap)
                e8_str = estimator.format_estimate(N, max_cycle_len=8, inject_trap=trap)
                t_base_est = cls.format_estimated_time(t_calib, 10, N)

                r_lap_p6, r_lap_t6 = [], []
                r_lap_p8, r_lap_t8 = [], []
                r_svd_p8, r_svd_t8 = [], []

                lap6_to_count, lap8_to_count, svd8_to_count = 0, 0, 0

                for _ in range(num_replicates):
                    R = ExchangeRateGenerator.generate(N, noise_level, trap, seed=None)

                    R_l6 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=6)
                    lp6, lt6, to_l6 = cls.run_dfs_with_timeout(R_l6, timeout=10.0)
                    if to_l6:
                        lap6_to_count += 1
                    else:
                        r_lap_p6.append(lp6)
                        r_lap_t6.append(lt6)

                    R_l8 = PruningAlgorithms.laplacian_induced_pruning(R, max_nodes=8)
                    lp8, lt8, to_l8 = cls.run_dfs_with_timeout(R_l8, timeout=10.0)
                    if to_l8:
                        lap8_to_count += 1
                    else:
                        r_lap_p8.append(lp8)
                        r_lap_t8.append(lt8)

                    R_s8 = PruningAlgorithms.svd_induced_pruning(R, max_nodes=8)
                    sp8, st8, to_s8 = cls.run_dfs_with_timeout(R_s8, timeout=10.0)
                    if to_s8:
                        svd8_to_count += 1
                    else:
                        r_svd_p8.append(sp8)
                        r_svd_t8.append(st8)

                valid_profits = []
                if r_lap_p6:
                    valid_profits.append(np.mean(r_lap_p6))
                if r_lap_p8:
                    valid_profits.append(np.mean(r_lap_p8))
                if r_svd_p8:
                    valid_profits.append(np.mean(r_svd_p8))
                max_profit_mean = max(valid_profits) if valid_profits else 0.0

                large_results.append({
                    "N": N,
                    "Trap": str(trap),
                    "Base Prof/Time": f"-- / Est: {t_base_est}",
                    "E≤6 (t)": e6_str,
                    "Lap-6Node Prof(Opt)/Time": cls.format_cell(
                        r_lap_p6, r_lap_t6, lap6_to_count,
                        is_large=True, max_empirical_p=max_profit_mean
                    ),
                    "E≤8 (t)": e8_str,
                    "Lap-8Node Prof(Opt)/Time": cls.format_cell(
                        r_lap_p8, r_lap_t8, lap8_to_count,
                        is_large=True, max_empirical_p=max_profit_mean
                    ),
                    "SVD-8Node Prof(Opt)/Time": cls.format_cell(
                        r_svd_p8, r_svd_t8, svd8_to_count,
                        is_large=True, max_empirical_p=max_profit_mean
                    ),
                })
        print(pd.DataFrame(large_results).to_markdown(index=False))

        # ==========================================
        # 理论估计器诊断：展示 trap=True 时理论最优项来自哪一类回路
        # ==========================================
        print("\n\n" + "=" * 120 + "\nTrapped Expectation 诊断：理论最大项来源\n" + "=" * 120)
        diag_rows = []
        for N in [8, 10, 50, 100, 200]:
            for L in [6, 8]:
                for trap in [False, True]:
                    profit, info = estimator.estimate_profit(N, max_cycle_len=L, inject_trap=trap)
                    trap_edge_str = "[]" if not info or not info["trap_edges"] else str(list(info["trap_edges"]))
                    diag_rows.append({
                        "N": N,
                        "MaxLen": L,
                        "Trap": str(trap),
                        "TheoryProfit": f"{profit * 100:.3f}%",
                        "DominantLen": info["cycle_len"] if info else None,
                        "TrapEdgesInDominantClass": trap_edge_str,
                        "CandidateCount": info["candidate_count"] if info else None,
                    })
        print(pd.DataFrame(diag_rows).to_markdown(index=False))

if __name__ == "__main__":
    ExperimentRunner.execute_suite()
