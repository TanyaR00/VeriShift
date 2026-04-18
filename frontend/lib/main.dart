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
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple, brightness: Brightness.dark),
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
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onItemTapped,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.upload_file),
            label: 'Upload',
          ),
          NavigationDestination(
            icon: Icon(Icons.compare_arrows),
            label: 'Twin Reality',
          ),
          NavigationDestination(
            icon: Icon(Icons.dashboard),
            label: 'Live Bias',
          ),
        ],
      ),
    );
  }
}
