import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
# p型材料表格数据的读入
print('请输入p型材料的参杂率：')
value_p = input()
print('请输入n型材料的参加率：')
value_n = input()

if value_p == '0.01':
    a1 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/P_yuanshi_0.01.xls', header=None).values
elif value_p == '0.02':
    a1 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/P_yuanshi_0.02.xls', header=None).values
elif value_p == '0.03':
    a1 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/P_yuanshi_0.03.xls', header=None).values

if value_n == '0.0004':
    a2 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/N_yuanshi_0.0004.xls', header=None).values
elif value_n == '0.0012':
    a2 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/N_yuanshi_0.0012.xls', header=None).values
elif value_n == '0.0020':
    a2 = pd.read_excel(r'/Users/zhaoshiyi/蓝桥云课/大学生物理竞赛/N_yuanshi_0.0020.xls', header=None).values
print('请输入N型和P型的横截面积比(N/P，输入数字范围（0-2.5)：')

area_ratio = float(input())
# 定义插值函数
def material_P(T):
    sb = CubicSpline(a1[:, 0], a1[:, 1])(T) * 1e-6  # 塞贝克系数
    res = CubicSpline(a1[:, 2], a1[:, 3])(T) * 1e-3  # 电导率
    ZT = CubicSpline(a1[:, 4], a1[:, 5])(T)  # 优值系数
    th = (T * sb ** 2) / (ZT * res)  # 热导率
    return sb, res, th

def material_N(T):
    sb = CubicSpline(a2[:, 0], a2[:, 1])(T) * 1e-6  # 塞贝克系数
    res = CubicSpline(a2[:, 2], a2[:, 3])(T) * 1e-3  # 电导率
    th = CubicSpline(a2[:, 4], a2[:, 5])(T) / 100  # 热导率
    return sb, res, th

def temperature_distribution_P(n, J, Tc, Th, max_iter):  # max_iter是迭代次数
    # 参数初始化
    l = 1
    dx = l / (n - 1)
    T = np.linspace(Tc, Th, n)
    # 迭代求解
    for _ in range(max_iter):
        A = np.zeros((n, n))  # A代表的是系数矩阵，b代表的是AX=b中有边的姐，我们要求的是X
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
        for i in range(1, n - 1):
            A[i, i - 1] = 1 / (c2[i] * dx)
            A[i, i] = c4[i + 1] / c2[i + 1] - 1 / (c2[i + 1] * dx) - (1 - c1[i] * dx) / (c2[i] * dx)
            A[i, i + 1] = (1 - c1[i + 1] * dx) / (c2[i + 1] * dx) - c3[i + 1] * dx - (1 - c1[i + 1] * dx) * c4[i + 1] / c2[i + 1]
            b[i] = c5[i - 1] * dx
        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            print("线性方程组求解失败，请检查系数矩阵。")
            return None
        T = T_new.copy()
    return T

def temperature_distribution_N(n, J, Tc, Th, max_iter):  # max_iter是迭代次数
    # 参数初始化
    l = 1
    dx = l / (n - 1)
    T = np.linspace(Tc, Th, n)
    # 迭代求解
    for _ in range(max_iter):
        A = np.zeros((n, n))  # A代表的是系数矩阵，b代表的是AX=b中有边的姐，我们要求的是X
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
        for i in range(1, n - 1):
            A[i, i - 1] = 1 / (c2[i] * dx)
            A[i, i] = c4[i + 1] / c2[i + 1] - 1 / (c2[i + 1] * dx) - (1 - c1[i] * dx) / (c2[i] * dx)
            A[i, i + 1] = (1 - c1[i + 1] * dx) / (c2[i + 1] * dx) - c3[i + 1] * dx - (1 - c1[i + 1] * dx) * c4[i + 1] / c2[i + 1]
            b[i] = c5[i - 1] * dx
        try:
            T_new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            print("线性方程组求解失败，请检查系数矩阵。")
            return None
        T = T_new.copy()
    return T

# 调用函数并打印结果
result_P = temperature_distribution_P(n=10, J=-1.5, Tc=300, Th=500, max_iter=10)
if result_P is not None:
    print(result_P)

result_N = temperature_distribution_N(n=10, J=25, Tc=300, Th=500, max_iter=10)
if result_N is not None:
    print(result_N)


def calculate_efficiency_P(Tc, Th, n, l):
    eff_list_P = []
    J_list_P = []
    dx = l / (n - 1)

    for j in range(0, 31, 1):
        J = -j
        T = temperature_distribution_P(n, J, Tc, Th, 10)
        sb, res, th = material_P(T)
        c1 = J * sb / th
        c2 = -1 / th
        c3 = sb ** 2 * J ** 2 / th
        c4 = -J * sb / th
        c5 = res * J ** 2

        # 计算热流密度, 定义为 q_P表示P的热流密度
        q_P = np.zeros(n)
        for k in range(1, n):
            q_P[k] = ((1 / dx - c1[k]) * T[k] - T[k - 1] / dx) / (c2[k])
        q_P[0] = (1 - c4[1] * dx) * q_P[1] - c3[1] * dx * T[1] - c5[1] * dx

        # 第一个积分
        Cumulative_scoring1 = 0
        # 第二个积分
        Cumulative_scoring2 = 0
        for m in range(1, n):
            T1 = T[m]
            T2 = T[m - 1]
            Cumulative_scoring1 += (sb[m] + sb[m - 1]) / 2 * (T1 - T2)
            Cumulative_scoring2 += (res[m] + res[m - 1]) / 2 * dx

        eff = J * (Cumulative_scoring1 + J * Cumulative_scoring2) / q_P[n - 1]
        eff_list_P.append(eff)
        J_list_P.append(J)

    return eff_list_P, J_list_P, q_P


def calculate_efficiency_N(Tc, Th, n, l):
    eff_list_N = []
    J_list_N = []
    dx = l / (n - 1)

    for j in range(0, 51, 1):
        J = j
        T = temperature_distribution_N(n, J, Tc, Th, 10)
        sb, res, th = material_N(T)
        c1 = J * sb / th
        c2 = -1 / th
        c3 = sb ** 2 * J ** 2 / th
        c4 = -J * sb / th
        c5 = res * J ** 2

        # 计算热流密度, 定义为 q_N表示N的热流密度
        q_N = np.zeros(n)
        for k in range(1, n):
            q_N[k] = ((1 / dx - c1[k]) * T[k] - T[k - 1] / dx) / (c2[k])
        q_N[0] = (1 - c4[1] * dx) * q_N[1] - c3[1] * dx * T[1] - c5[1] * dx

        # 第一个积分
        Cumulative_scoring1 = 0
        # 第二个积分
        Cumulative_scoring2 = 0
        for m in range(1, n):
            T1 = T[m]
            T2 = T[m - 1]
            Cumulative_scoring1 += (sb[m] + sb[m - 1]) / 2 * (T1 - T2)
            Cumulative_scoring2 += (res[m] + res[m - 1]) / 2 * dx

        eff = J * (Cumulative_scoring1 + J * Cumulative_scoring2) / q_N[n - 1]
        eff_list_N.append(eff)
        J_list_N.append(J)
    return eff_list_N, J_list_N, q_N

eff_list_P, J_list_P, q_P = calculate_efficiency_P(300, 500, 10, 1)
eff_list_N, J_list_N, q_N = calculate_efficiency_N(300, 500, 10, 1)


def calculate_total(area_ratio):
    eff_total_list = []
    I_list = []
    for m in range(1, 21, 1):  # m代表电流密度，在P型中由于单位横截面积就是1cm^2，故用电流密度代替电流
        I_list.append(m)
        index_N = int(m * area_ratio)
        if m < len(eff_list_P) and index_N < len(eff_list_N):
            denominator = q_P[-1] / m - q_N[-1] / (m / area_ratio)
            if denominator != 0:
                eff_total = (eff_list_P[m - 1] * q_P[-1] / m - eff_list_N[index_N] * q_N[-1] / (m / area_ratio)) / denominator
                eff_total_list.append(eff_total)
    return I_list, eff_total_list


I_list, eff_total_list = calculate_total(area_ratio)


def Power_total(area_ratio):
    Power_total_list = []
    I_list, eff_total_list = calculate_total(area_ratio)
    for n in range(0, len(eff_total_list)):
        pow_total = eff_total_list[n] * (q_P[-1] + q_N[-1] * area_ratio)
        Power_total_list.append(pow_total)
    return Power_total_list

def plot_data(x_list, y_list, x_label, y_label, title):
    plt.plot(x_list, y_list)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()

#绘制分支P效率随着电流密度的变化
plot_data(J_list_P, eff_list_P,'J','eff','P')

#绘制分支N效率随着电流密度的变化
plot_data(J_list_N, eff_list_N,'J','eff','N')


#绘制总效率随着电流的改变
plot_data(I_list, eff_total_list,'I','eff','total')
plt.show()

#绘制总功率随电流的改变而改变
Power_total_list = Power_total(area_ratio)
plot_data(I_list, Power_total_list,'I','Power','total')
