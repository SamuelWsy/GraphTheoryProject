import numpy as np
import math
import time
from collections import deque
import pandas as pd

# ==========================================
# 模块 1：基础图与算法模块 (静默模式，去除print)
# ==========================================
class Edge:
    def __init__(self, to, weight, rate):
        self.to = to
        self.w = weight
        self.rate = rate

class ArbitrageGraph:
    def __init__(self, n):
        self.N = n
        self.adj = [[] for _ in range(n)]

    def add_edge(self, fr, to, rate):
        if rate <= 0: return
        w = -math.log(rate)
        self.adj[fr].append(Edge(to, w, rate))

    def find_arbitrage(self):
        dist = [0.0] * self.N
        pre = [-1] * self.N
        cnt = [0] * self.N
        inqueue = [False] * self.N
        q = deque(range(self.N))
        for i in range(self.N): inqueue[i] = True

        while q:
            u = q.popleft()
            inqueue[u] = False
            for e in self.adj[u]:
                v = e.to
                if dist[v] > dist[u] + e.w + 1e-9:
                    dist[v] = dist[u] + e.w
                    pre[v] = u
                    if not inqueue[v]:
                        cnt[v] += 1
                        if cnt[v] >= self.N:
                            path = []
                            vis = dict()
                            cur = v
                            while True:
                                if cur in vis:
                                    idx = vis[cur]
                                    return path[idx:][::-1]
                                vis[cur] = len(path)
                                path.append(cur)
                                cur = pre[cur]
                        inqueue[v] = True
                        q.append(v)
        return None

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
# 模块 2：数据生成与剪枝算法
# ==========================================
class ExchangeRateGenerator:
    @staticmethod
    def generate(N, noise_level, inject_trap):
        prices = np.random.uniform(0.5, 5.0, N)
        R = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    ideal_rate = prices[j] / prices[i]
                    noise = np.random.uniform(-noise_level, noise_level)
                    R[i, j] = ideal_rate * (1 + noise)
        if inject_trap and N >= 4:
            # 注入隐蔽微亏长链陷阱
            R[0, 1] = (prices[1]/prices[0]) * 1.04
            R[1, 2] = (prices[2]/prices[1]) * 1.04
            R[2, 3] = (prices[3]/prices[2]) * 1.04
            R[3, 0] = (prices[0]/prices[3]) * 0.98
        return R

class PruningAlgorithms:
    @staticmethod
    def laplacian_pruning(R, delta_threshold=0.001):
        N = R.shape[0]
        M = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j and R[i, j] > 0: M[i, j] = math.log(R[i, j])
        
        y = np.mean(M, axis=0)
        Delta_M = np.zeros((N, N))
        hot_nodes = set()
        
        for i in range(N):
            for j in range(N):
                if i != j:
                    Delta_M[i, j] = M[i, j] - (y[j] - y[i])
                    if Delta_M[i, j] > delta_threshold:
                        hot_nodes.add(i)
                        hot_nodes.add(j)
                        
        R_pruned = np.zeros_like(R)
        for i in hot_nodes:
            for j in hot_nodes:
                if i != j: R_pruned[i, j] = R[i, j]
        return R_pruned

    @staticmethod
    def svd_sinkhorn_pruning(R, retain_ratio=0.10):
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
# 模块 3：批量测试与指标聚合框架
# ==========================================
def run_single_algo(R):
    N = R.shape[0]
    g = ArbitrageGraph(N)
    edge_count = 0
    for i in range(N):
        for j in range(N):
            if R[i, j] > 0:
                g.add_edge(i, j, R[i, j])
                edge_count += 1
                
    start_t = time.perf_counter()
    loop = g.find_arbitrage()
    end_t = time.perf_counter()
    
    profit = g.calc_profit(loop) if loop else 0.0
    return profit, (end_t - start_t) * 1000, edge_count

def run_batch_experiments():
    # 参数空间设定
    N_list = [100, 300]              # 矩阵阶数
    noise_list = [0.002, 0.01]       # 市场波动率 (低波动, 高波动)
    trap_list = [False, True]        # 是否注入长链微亏陷阱
    num_trials = 10                  # 每种组合进行的随机试验次数
    
    results = []
    total_iters = len(N_list) * len(noise_list) * len(trap_list)
    curr_iter = 0

    print("开始进行蒙特卡洛批量稳定性测试...")
    for N in N_list:
        for noise in noise_list:
            for trap in trap_list:
                curr_iter += 1
                print(f"进度: {curr_iter}/{total_iters} | N={N}, Noise={noise}, Trap={trap}")
                
                # 临时存储当次组合中各 trial 的数据
                trial_data = {'Base_P':[], 'Base_T':[], 'Lap_P':[], 'Lap_T':[], 'SVD_P':[], 'SVD_T':[]}
                
                for _ in range(num_trials):
                    R = ExchangeRateGenerator.generate(N, noise, trap)
                    
                    # 1. 基准全图 (Ground Truth)
                    prof_base, t_base, _ = run_single_algo(R)
                    
                    # 2. Laplacian 剪枝
                    start_prune_l = time.perf_counter()
                    R_lap = PruningAlgorithms.laplacian_pruning(R, delta_threshold=0.001)
                    t_prune_l = (time.perf_counter() - start_prune_l) * 1000
                    prof_lap, t_search_l, _ = run_single_algo(R_lap)
                    
                    # 3. SVD 剪枝
                    start_prune_s = time.perf_counter()
                    R_svd = PruningAlgorithms.svd_sinkhorn_pruning(R, retain_ratio=0.1)
                    t_prune_s = (time.perf_counter() - start_prune_s) * 1000
                    prof_svd, t_search_s, _ = run_single_algo(R_svd)
                    
                    # 记录数据 (时间记录：剪枝 + 寻路总时间)
                    trial_data['Base_P'].append(prof_base)
                    trial_data['Base_T'].append(t_base)
                    
                    # 计算相对最优性 (Relative Optimality)
                    opt_lap = (prof_lap / prof_base) if prof_base > 0 else (1.0 if prof_lap == 0 else 0.0)
                    trial_data['Lap_P'].append(opt_lap)
                    trial_data['Lap_T'].append(t_prune_l + t_search_l)
                    
                    opt_svd = (prof_svd / prof_base) if prof_base > 0 else (1.0 if prof_svd == 0 else 0.0)
                    trial_data['SVD_P'].append(opt_svd)
                    trial_data['SVD_T'].append(t_prune_s + t_search_s)

                # 聚合本组合的均值和标准差
                results.append({
                    'N': N, 'Noise': noise, 'Trap': str(trap),
                    'Base Time (ms)': f"{np.mean(trial_data['Base_T']):.1f}±{np.std(trial_data['Base_T']):.1f}",
                    
                    'Lap Opt(%)': f"{np.mean(trial_data['Lap_P'])*100:.1f}±{np.std(trial_data['Lap_P'])*100:.1f}",
                    'Lap Time (ms)': f"{np.mean(trial_data['Lap_T']):.1f}±{np.std(trial_data['Lap_T']):.1f}",
                    
                    'SVD Opt(%)': f"{np.mean(trial_data['SVD_P'])*100:.1f}±{np.std(trial_data['SVD_P'])*100:.1f}",
                    'SVD Time (ms)': f"{np.mean(trial_data['SVD_T']):.1f}±{np.std(trial_data['SVD_T']):.1f}"
                })

    # 生成 Markdown 表格
    df = pd.DataFrame(results)
    print("\n\n" + "="*80)
    print("实验结果稳定性统计汇总表 (Markdown格式)")
    print("="*80)
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    run_batch_experiments()