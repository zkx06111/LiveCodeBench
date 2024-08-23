#include <iostream>
using namespace std;

int main() {
    int n;
    string s;
    cin >> n >> s;
    string winner = "";
    int cnt_t = 0, cnt_a = 0;
    for (auto c: s) {
        if (c == 'T') ++cnt_t;
        if (c == 'A') ++cnt_a;
        if (cnt_t > cnt_a) winner = "T";
        else if (cnt_t < cnt_a) winner = "A";
    }
    cout << winner << endl;
    return 0;
}