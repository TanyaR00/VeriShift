import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class LiveBiasDashboardScreen extends StatefulWidget {
  const LiveBiasDashboardScreen({super.key});

  @override
  State<LiveBiasDashboardScreen> createState() =>
      _LiveBiasDashboardScreenState();
}

class _LiveBiasDashboardScreenState extends State<LiveBiasDashboardScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Container(width: 4, height: 20, color: const Color(0xFF00BFA5)),
        const SizedBox(width: 12),
        Text(title,
            style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: Colors.white)),
      ],
    );
  }

  Widget _buildMetricCard(String label, Widget valueWidget) {
    return Expanded(
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF141420),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.transparent),
        ),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(label,
                style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.0)),
            const SizedBox(height: 12),
            valueWidget,
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
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
      appBar: AppBar(
        title: Row(
          children: const [
            Icon(Icons.verified_user, color: Color(0xFF00BFA5)),
            SizedBox(width: 8),
            Text('VeriShift'),
          ],
        ),
        actions: [
          Center(
            child: Container(
              margin: const EdgeInsets.only(right: 16),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF1A0500),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  FadeTransition(
                    opacity: _pulseController,
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                          color: Color(0xFFFF5252), shape: BoxShape.circle),
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text('LIVE',
                      style: TextStyle(
                          color: Color(0xFFFF5252),
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.0)),
                ],
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader('Bias Trend'),
            const SizedBox(height: 16),
            SizedBox(
              height: 300,
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF141420),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                      color: Colors.white.withOpacity(0.15), width: 1),
                ),
                padding: const EdgeInsets.all(16.0),
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF0D0D1A),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  padding: const EdgeInsets.only(right: 16, top: 16, bottom: 8),
                  child: LineChart(
                    LineChartData(
                      gridData: FlGridData(
                        show: true,
                        drawVerticalLine: true,
                        getDrawingHorizontalLine: (value) => FlLine(
                            color: Colors.white.withOpacity(0.05),
                            strokeWidth: 1),
                        getDrawingVerticalLine: (value) => FlLine(
                            color: Colors.white.withOpacity(0.05),
                            strokeWidth: 1),
                      ),
                      titlesData: const FlTitlesData(
                        rightTitles: AxisTitles(
                            sideTitles: SideTitles(showTitles: false)),
                        topTitles: AxisTitles(
                            sideTitles: SideTitles(showTitles: false)),
                        leftTitles: AxisTitles(
                            sideTitles:
                                SideTitles(showTitles: true, reservedSize: 40)),
                        bottomTitles: AxisTitles(
                            sideTitles:
                                SideTitles(showTitles: true, reservedSize: 30)),
                      ),
                      borderData: FlBorderData(show: false),
                      extraLinesData: ExtraLinesData(verticalLines: [
                        VerticalLine(
                          x: 0,
                          color: Colors.white.withOpacity(0.3),
                          strokeWidth: 1,
                          dashArray: [4, 4],
                          label: VerticalLineLabel(
                              show: true,
                              labelResolver: (line) => 'Phase 1',
                              style: const TextStyle(
                                  color: Colors.grey, fontSize: 10),
                              alignment: Alignment.topRight),
                        ),
                        VerticalLine(
                          x: 6.5,
                          color: Colors.white.withOpacity(0.3),
                          strokeWidth: 1,
                          dashArray: [4, 4],
                          label: VerticalLineLabel(
                              show: true,
                              labelResolver: (line) => 'Phase 2',
                              style: const TextStyle(
                                  color: Colors.grey, fontSize: 10),
                              alignment: Alignment.topRight),
                        ),
                        VerticalLine(
                          x: 13,
                          color: Colors.white.withOpacity(0.3),
                          strokeWidth: 1,
                          dashArray: [4, 4],
                          label: VerticalLineLabel(
                              show: true,
                              labelResolver: (line) => 'Phase 3',
                              style: const TextStyle(
                                  color: Colors.grey, fontSize: 10),
                              alignment: Alignment.topRight),
                        ),
                      ]),
                      lineBarsData: [
                        LineChartBarData(
                          spots: spots,
                          isCurved: true,
                          color: const Color(0xFFFF5252),
                          barWidth: 3,
                          isStrokeCapRound: true,
                          dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(
                              show: true,
                              color: const Color(0xFFFF5252).withOpacity(0.08)),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF141420),
                borderRadius: BorderRadius.circular(12),
                border:
                    Border.all(color: Colors.white.withOpacity(0.10), width: 1),
              ),
              child: Row(
                children: [
                  _buildMetricCard(
                      'BIAS SCORE',
                      Column(
                        children: [
                          const Text('0.85',
                              style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFFFF5252))),
                          const SizedBox(height: 8),
                          SizedBox(
                            width: 40,
                            height: 12,
                            child: CustomPaint(
                                painter: SparklinePainter(
                                    color: const Color(0xFFFF5252))),
                          ),
                        ],
                      )),
                  Container(
                      width: 1,
                      height: 60,
                      color: Colors.white.withOpacity(0.10)),
                  _buildMetricCard(
                      'AFFECTED GROUP',
                      const Text('Female',
                          style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white))),
                  Container(
                      width: 1,
                      height: 60,
                      color: Colors.white.withOpacity(0.10)),
                  _buildMetricCard(
                      'TREND',
                      const Icon(Icons.trending_up,
                          color: Color(0xFFFFB300), size: 32)),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1A1500),
                border: const Border(
                    left: BorderSide(color: Color(0xFFFFB300), width: 4)),
                borderRadius: const BorderRadius.only(
                    topRight: Radius.circular(8),
                    bottomRight: Radius.circular(8)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      FadeTransition(
                        opacity: _pulseController,
                        child: Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                              color: Color(0xFFFF5252), shape: BoxShape.circle),
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Text(
                          '⚠ Bias increasing against female group in last 24 hours',
                          style: TextStyle(
                              color: Color(0xFFFFB300),
                              fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Padding(
                    padding: EdgeInsets.only(left: 20),
                    child: Text(
                      'Last updated: just now · Auto-refreshes every 30s',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
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

class SparklinePainter extends CustomPainter {
  final Color color;

  SparklinePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final path = Path();
    path.moveTo(0, size.height);
    path.lineTo(size.width * 0.25, size.height * 0.8);
    path.lineTo(size.width * 0.5, size.height * 0.9);
    path.lineTo(size.width * 0.75, size.height * 0.4);
    path.lineTo(size.width, 0);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
