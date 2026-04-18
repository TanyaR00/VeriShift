import 'package:flutter/material.dart';
import 'screens/upload_dataset_screen.dart';
import 'screens/twin_simulation_screen.dart';
import 'screens/live_bias_dashboard_screen.dart';

void main() {
  runApp(const VeriShiftApp());
}

class VeriShiftApp extends StatelessWidget {
  const VeriShiftApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VeriShift',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A0F),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00BFA5),
          surface: Color(0xFF141420),
          background: Color(0xFF0A0A0F),
        ),
        fontFamily: 'Inter', // Fallback to system sans-serif if not installed
        appBarTheme: AppBarTheme(
          backgroundColor: const Color(0xFF0A0A0F),
          elevation: 0,
          shape: Border(
            bottom: BorderSide(
              color: Colors.white.withOpacity(0.08),
              width: 1,
            ),
          ),
          iconTheme: const IconThemeData(color: Color(0xFF00BFA5)),
          titleTextStyle: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF00BFA5),
            foregroundColor: const Color(0xFF0A0A0F),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            elevation: 0,
          ),
        ),
        useMaterial3: true,
      ),
      home: const MainNavigation(),
    );
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const UploadDatasetScreen(),
    const TwinSimulationScreen(),
    const LiveBiasDashboardScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF0A0A0F),
          border: Border(
            top: BorderSide(
              color: Colors.white.withOpacity(0.08),
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          currentIndex: _selectedIndex,
          onTap: _onItemTapped,
          selectedItemColor: const Color(0xFF00BFA5),
          unselectedItemColor: Colors.grey,
          showUnselectedLabels: true,
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.upload_file),
              label: 'Upload',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.compare_arrows),
              label: 'Twin Reality',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.monitoring),
              label: 'Live Bias',
            ),
          ],
        ),
      ),
    );
  }
}
