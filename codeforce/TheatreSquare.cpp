#include <bits/stdc++.h>
using namespace std;

int main()
{
    long long n, m, a;
    cin >> n >> m >> a;

    long long soVienTheoChieuDai = (n + a - 1) / a;
    long long soVienTheoChieuRong = (m + a - 1) / a;

    long long tongSoVien = soVienTheoChieuDai * soVienTheoChieuRong;

    cout << tongSoVien;

    return 0;
}