import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import matplotlib as mpl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取P型材料数据
a1 = pd.read_excel('P_yuanshi_2_5.xls', header=None).values
print("P型材料数据:")
print("温度\t塞贝克系数\t电导率\tZT")
for row in a1[:5]:
    print(f"{row[0]:.1f}\t{row[1]:.2e}\t{row[2]:.2e}\t{row[4]:.2f}")

# 读取N型材料数据
a2 = pd.read_excel('N_yuanshi_0.0004.xls', header=None).values
print("\nN型材料数据:")
print("温度\t塞贝克系数\t电导率\tZT")
for row in a2[:5]:
    print(f"{row[0]:.1f}\t{row[1]:.2e}\t{row[2]:.2e}\t{row[4]:.2f}")

def material_P(T):
    """计算P型材料属性"""
    sb = CubicSpline(a1[:, 0], a1[:, 1])(T) * 1e-6  # 塞贝克系数
    res = CubicSpline(a1[:, 2], a1[:, 3])(T) * 1e-3  # 电导率
    ZT = CubicSpline(a1[:, 4], a1[:, 5])(T)  # 优值系数
    th = (T * sb ** 2) / (ZT * res)  # 热导率
    return sb, res, th

def material_N(T):
    """计算N型材料属性"""
    sb = CubicSpline(a2[:, 0], a2[:, 1])(T) * 1e-6  # 塞贝克系数，单位：V/K
    res = CubicSpline(a2[:, 2], a2[:, 3])(T) * 1e-3  # 电导率，单位：S/m
    th = CubicSpline(a2[:, 4], a2[:, 5])(T)/100  # 热导率，单位：W/(m·K)
    return sb, res, th

def temperature_distribution_P(n, J, Tc, Th, max_iter):
    """计算P型材料温度分布"""
    l = 1
    dx = l / (n - 1)
    T = np.linspace(Tc, Th, n)
    
    for _ in range(max_iter):
        A = np.zeros((n, n))
        b = np.zeros(n)
        sb, res, th = material_P(T)
        
        c1 = J * sb / th
        c2 = -1 / th
        c3 = sb ** 2 * J ** 2 / th
        c4 = -J * sb / th
        c5 = res * J ** 2
        
        # 边界条件
        A[0, 0] = 1
        b[0] = Tc
        A[-1, -1] = 1
        b[-1] = Th
        
        # 构造系数矩阵
        for i in range(1, n-1):
            A[i, i-1] = 1/(c2[i] * dx)
            A[i, i] = c4[i+1]/c2[i+1] - 1/(c2[i+1] * dx) - (1 - c1[i] * dx)/(c2[i] * dx)
            A[i, i+1] = (1 - c1[i+1] * dx)/(c2[i+1] * dx) - c3[i+1] * dx - (1 - c1[i+1] * dx) * c4[i+1]/c2[i+1]
            b[i] = c5[i-1] * dx
            
        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            print("线性方程组求解失败")
            return None
            
        T = T_new.copy()
        
    return T

def temperature_distribution_N(n, J, Tc, Th, max_iter):
    """计算N型材料温度分布"""
    l = 1
    dx = l / (n - 1)
    T = np.linspace(Tc, Th, n)
    
    for _ in range(max_iter):
        A = np.zeros((n, n))
        b = np.zeros(n)
        sb, res, th = material_N(T)
        
        c1 = J * sb / th
        c2 = -1 / th
        c3 = sb ** 2 * J ** 2 / th
        c4 = -J * sb / th
        c5 = res * J ** 2
        
        # 边界条件
        A[0, 0] = 1
        b[0] = Tc
        A[-1, -1] = 1
        b[-1] = Th
        
        # 构造系数矩阵
        for i in range(1, n-1):
            A[i, i-1] = 1/(c2[i] * dx)
            A[i, i] = c4[i+1]/c2[i+1] - 1/(c2[i+1] * dx) - (1 - c1[i] * dx)/(c2[i] * dx)
            A[i, i+1] = (1 - c1[i+1] * dx)/(c2[i+1] * dx) - c3[i+1] * dx - (1 - c1[i+1] * dx) * c4[i+1]/c2[i+1]
            b[i] = c5[i-1] * dx
            
        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            print("线性方程组求解失败")
            return None
            
        T = T_new.copy()
        
    return T

def calculate_efficiency_P(Tc, Th, n, l):
    """计算P型材料效率"""
    eff_list_P = []
    J_list_P = []
    dx = l / (n - 1)
    
    for j in range(0, 31, 2):
        J = -j
        print(f"\n计算P型效率 (J={J}A/cm²)")
        
        T = temperature_distribution_P(n, J, Tc, Th, 10)
        if T is None:
            print("温度分布计算失败")
            continue
            
        sb, res, th = material_P(T)
        
        # 计算热流密度q
        q = np.zeros(n)
        for k in range(1, n):
            q[k] = ((1/dx - J*sb[k]/th[k]) * T[k] - T[k-1]/dx) / (-1/th[k])
        q[0] = (1 - (-J*sb[1]/th[1]) * dx) * q[1] - (sb[1]**2 * J**2/th[1]) * dx * T[1] - (res[1] * J**2) * dx
        
        # 计算积分项
        seebeck_integral = 0
        resistivity_integral = 0
        for m in range(1, n):
            T1 = T[m]
            T2 = T[m-1]
            seebeck_integral += (sb[m] + sb[m-1]) / 2 * (T1 - T2)
            resistivity_integral += (res[m] + res[m-1]) / 2 * dx
            
        print(f"塞贝克积分: {seebeck_integral:.6f} V")
        print(f"电阻率积分: {resistivity_integral:.6f} Ω·m")
        
        if q[n-1] != 0:
            eff = J * (seebeck_integral + J * resistivity_integral) / q[n-1]
            print(f"计算效率: {eff:.6f}")
            eff_list_P.append(eff)
            J_list_P.append(J)
        else:
            print("热流为零，跳过此点")
            
    return eff_list_P, J_list_P

def calculate_efficiency_N(Tc, Th, n, l):
    """计算N型材料效率"""
    eff_list_N = []
    J_list_N = []
    dx = l / (n - 1)
    
    # 测试N型材料的电流密度范围，从0到50
    for j in range(0, 51, 1):
        J = j
        print(f"\n计算N型效率 (J={J}A/cm²)")
        
        T = temperature_distribution_N(n, J, Tc, Th, 10)
        if T is None:
            print("温度分布计算失败")
            continue
            
        sb, res, th = material_N(T)
        
        # 计算热流系数
        c1 = J * sb / th
        c2 = -1 / th
        c3 = sb ** 2 * J ** 2 / th
        c4 = -J * sb / th
        c5 = res * J ** 2
        
        # 计算热流密度q
        q = np.zeros(n)
        for k in range(1, n):
            q[k] = ((1/dx - c1[k]) * T[k] - T[k-1]/dx) / (c2[k])
        q[0] = (1 - c4[1] * dx) * q[1] - c3[1] * dx * T[1] - c5[1] * dx
        
        # 计算积分项
        Cumulative_scoring1 = 0
        Cumulative_scoring2 = 0
        for m in range(1, n):
            T1 = T[m]
            T2 = T[m-1]
            Cumulative_scoring1 += (sb[m] + sb[m-1]) / 2 * (T1 - T2)
            Cumulative_scoring2 += (res[m] + res[m-1]) / 2 * dx
            
        print(f"塞贝克积分: {Cumulative_scoring1:.6f} V")
        print(f"电阻率积分: {Cumulative_scoring2:.6f} Ω·m")
        
        # 计算效率
        if q[n-1] != 0:
            eff = J * (Cumulative_scoring1 + J * Cumulative_scoring2) / q[n-1]
            print(f"计算效率: {eff:.6f}")
            
            # 检查效率是否超过卡诺效率
            carnot_eff = 1 - Tc / Th
            if abs(eff) > carnot_eff:
                print(f"警告: 计算效率 {eff:.6f} 超过卡诺效率 {carnot_eff:.6f}")
                
            eff_list_N.append(eff)
            J_list_N.append(J)
        else:
            print("热流为零，跳过此点")
            
    return eff_list_N, J_list_N

# 测试计算
if __name__ == "__main__":
    Tc = 300
    Th = 500
    n = 10
    l = 1.0
    
    print(f"开始计算P型材料效率曲线: Tc={Tc}K, Th={Th}K")
    eff_list_P, J_list_P = calculate_efficiency_P(Tc, Th, n, l)
    
    print("\nP型效率结果:", eff_list_P)
    print("P型电流密度:", J_list_P)
    
    # 绘制P型效率曲线
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(J_list_P, eff_list_P, 'b-')
    plt.xlabel('电流密度 (A/cm2)')
    plt.ylabel('效率')
    plt.title('P型材料效率曲线')
    plt.grid(True)
    
    print(f"\n开始计算N型材料效率曲线: Tc={Tc}K, Th={Th}K")
    eff_list_N, J_list_N = calculate_efficiency_N(Tc, Th, n, l)
    
    print("\nN型效率结果:", eff_list_N)
    print("N型电流密度:", J_list_N)
    
    # 绘制N型效率曲线
    plt.subplot(1, 2, 2)
    plt.plot(J_list_N, eff_list_N, 'r-')
    plt.xlabel('电流密度 (A/cm2)')
    plt.ylabel('效率')
    plt.title('N型材料效率曲线')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show() 