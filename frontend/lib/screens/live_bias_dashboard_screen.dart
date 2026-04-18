import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class LiveBiasDashboardScreen extends StatelessWidget {
  const LiveBiasDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Mock data for the bias trend line chart
    final spots = [
      const FlSpot(0, 0.05),
      const FlSpot(2, 0.04),
      const FlSpot(4, 0.06),
      const FlSpot(6, 0.08),
      const FlSpot(8, 0.12),
      const FlSpot(10, 0.20),
      const FlSpot(12, 0.25),
      const FlSpot(14, 0.35),
      const FlSpot(16, 0.45),
      const FlSpot(18, 0.60),
      const FlSpot(20, 0.85),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Live Bias Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Bias Trend', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            SizedBox(
              height: 300,
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: LineChart(
                    LineChartData(
                      gridData: const FlGridData(show: true),
                      titlesData: const FlTitlesData(
                        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      ),
                      borderData: FlBorderData(show: true),
                      lineBarsData: [
                        LineChartBarData(
                          spots: spots,
                          isCurved: true,
                          color: Colors.redAccent,
                          barWidth: 4,
                          isStrokeCapRound: true,
                          dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: true, color: Colors.redAccent.withOpacity(0.2)),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: const [
                          Text('Bias Score', style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 8),
                          Text('0.85', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.red)),
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: const [
                          Text('Affected Group', style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 8),
                          Text('Female', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: const [
                          Text('Trend', style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 8),
                          Icon(Icons.trending_up, color: Colors.red, size: 32),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.amber.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber.shade400),
              ),
              child: Row(
                children: const [
                  Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 32),
                  SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      '⚠ Bias increasing against female group in last 24 hours',
                      style: TextStyle(color: Colors.deepOrange, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
