#Trang Sĩ Hoàng 24162035
def Doi_xu(N, S):
    dp = [0] * (N + 1)
    dp[0] = 1
    for coin in S:
        for i in range(coin, N + 1):
            dp[i] = dp[i] + dp[i - coin]
    return dp[N]

N1 = 4
S1 = [1, 2, 3]
result1 = Doi_xu(N1, S1)
print(f"Với N = {N1} và S = {S1}: Số cách đổi là {result1}") 

N2 = 10
S2 = [2, 5, 3, 6]
result2 = Doi_xu(N2, S2)
print(f"Với N = {N2} và S = {S2}: Số cách đổi là {result2}") 
