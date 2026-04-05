#include <iostream>
using namespace std;

int main() {

    // Geometry of the robot and sensors
    double H;   // distance of the top sensor to ground
    double h1;  // distance of the top sensor to robot center
    double h2;  // distance of the ground to robot center
    double w1;  // distance of the left sensor to robot center
    double w2;  // distance of the right sensor to robot center
    double l;   // distance of the 45-degree sensor to robot center

    // Measured distances from sensors
    double d1;  // left sensor
    double d2;  // top sensor
    double d3;  // 45-degree sensor
    double d4;  // right sensor

    // ---- Input ----
    cout << "Enter sensor geometry:\n";
    cout << "H  = "; cin >> H;
    cout << "h1 = "; cin >> h1;
    cout << "h2 = "; cin >> h2;
    cout << "w1 = "; cin >> w1;
    cout << "w2 = "; cin >> w2;
    cout << "l  = "; cin >> l;

    cout << "\nEnter sensor readings:\n";
    cout << "d1 (left)      = "; cin >> d1;
    cout << "d2 (top)       = "; cin >> d2;
    cout << "d3 (45 degree) = "; cin >> d3;
    cout << "d4 (right)     = "; cin >> d4;

    // ---- Display (for checking) ----
    cout << "\n--- Input summary ---\n";
    cout << "H  = " << H  << endl;
    cout << "h1 = " << h1 << endl;
    cout << "h2 = " << h2 << endl;
    cout << "w1 = " << w1 << endl;
    cout << "w2 = " << w2 << endl;
    cout << "l  = " << l  << endl;

    cout << "d1 = " << d1 << endl;
    cout << "d2 = " << d2 << endl;
    cout << "d3 = " << d3 << endl;
    cout << "d4 = " << d4 << endl;

    return 0;
}