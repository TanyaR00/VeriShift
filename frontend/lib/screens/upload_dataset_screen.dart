import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class UploadDatasetScreen extends StatefulWidget {
  const UploadDatasetScreen({super.key});

  @override
  State<UploadDatasetScreen> createState() => _UploadDatasetScreenState();
}

class _UploadDatasetScreenState extends State<UploadDatasetScreen> with SingleTickerProviderStateMixin {
  String? _selectedFileName;
  int _selectedFileSize = 0;
  Uint8List? _selectedFileBytes;

  bool _isAnalyzing = false;
  bool _isSuccess = false;
  bool _isHovering = false;
  
  // Dynamic metrics from backend
  List<String> _detectedAttributes = [];
  double _biasScore = 0.0;
  double _missingPercentage = 0.0;

  late AnimationController _bgAnimationController;

  @override
  void initState() {
    super.initState();
    _bgAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    )..repeat();
  }

  @override
  void dispose() {
    _bgAnimationController.dispose();
    super.dispose();
  }

  void _pickFile() {
    final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
    uploadInput.accept = '.csv';
    uploadInput.click();

    uploadInput.onChange.listen((e) {
      final files = uploadInput.files;
      if (files != null && files.isNotEmpty) {
        final file = files[0];
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Please select a valid .csv file'),
                backgroundColor: Color(0xFFFF5252),
              ),
            );
          }
          return;
        }

        final reader = html.FileReader();
        reader.readAsArrayBuffer(file);
        reader.onLoadEnd.listen((e) {
          if (mounted) {
            setState(() {
              _selectedFileName = file.name;
              _selectedFileSize = file.size;
              _selectedFileBytes = reader.result as Uint8List?;
              _isSuccess = false;
            });
          }
        });
      }
    });
  }

  Future<void> _processUpload() async {
    if (_selectedFileName == null || _selectedFileBytes == null) return;

    setState(() {
      _isAnalyzing = true;
    });

    try {
      await uploadDatasetToBackend();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error analyzing dataset: $e'),
            backgroundColor: const Color(0xFFFF5252),
          ),
        );
      }
    }

    if (mounted) {
      setState(() {
        _isAnalyzing = false;
        _isSuccess = true;
      });
    }
  }

  Future<void> uploadDatasetToBackend() async {
    var request = http.MultipartRequest('POST', Uri.parse('http://127.0.0.1:8000/upload-dataset'));
    request.files.add(http.MultipartFile.fromBytes('file', _selectedFileBytes!, filename: _selectedFileName!));
    
    var response = await request.send();
    if (response.statusCode == 200) {
      final respStr = await response.stream.bytesToString();
      final data = jsonDecode(respStr);
      
      setState(() {
        _detectedAttributes = List<String>.from(data['sensitive_attributes'] ?? []);
        _missingPercentage = (data['missing_percentage'] ?? 0.0).toDouble();
        _biasScore = (data['bias_score'] ?? 0.0).toDouble();
      });
    } else {
      throw Exception('Failed to upload dataset');
    }
  }

  String _formatBytes(int bytes) {
    if (bytes <= 0) return "0 B";
    const suffixes = ["B", "KB", "MB", "GB", "TB"];
    var i = (bytes.toString().length - 1) ~/ 3;
    return '${(bytes / pow(1024, i)).toStringAsFixed(1)} ${suffixes[i]}';
  }

  String _getBiasRiskLevel(double score) {
    if (score < 0.1) return 'Low';
    if (score < 0.3) return 'Moderate';
    return 'High';
  }
  
  Color _getBiasRiskColor(double score) {
    if (score < 0.1) return const Color(0xFF66BB6A);
    if (score < 0.3) return const Color(0xFFFFB300);
    return const Color(0xFFEF5350);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A0A0F),
        elevation: 0,
        title: Row(
          children: const [
            Icon(Icons.verified_user, color: Color(0xFF00BFA5)),
            SizedBox(width: 8),
            Text('VeriShift', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
      body: Stack(
        children: [
          // Background Animation
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _bgAnimationController,
              builder: (context, child) {
                return CustomPaint(
                  painter: _DataVisualizationBackgroundPainter(
                    animationValue: _bgAnimationController.value,
                  ),
                );
              },
            ),
          ),
          
          // Main Content
          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Container(
                width: double.infinity,
                constraints: const BoxConstraints(maxWidth: 600),
                decoration: BoxDecoration(
                  color: const Color(0xFF141420),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white.withOpacity(0.15), width: 1),
                ),
                padding: const EdgeInsets.all(40.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Drop Zone
                    Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: (_isAnalyzing || _isSuccess) ? null : _pickFile,
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 24),
                          decoration: BoxDecoration(
                            color: const Color(0xFF0A0A0F),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: _selectedFileName != null ? const Color(0xFF00BFA5) : Colors.white.withOpacity(0.15),
                              width: _selectedFileName != null ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            children: [
                              Icon(
                                _selectedFileName != null ? Icons.insert_drive_file : Icons.cloud_upload_outlined,
                                size: 48,
                                color: const Color(0xFF00BFA5),
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _selectedFileName != null ? _selectedFileName! : 'Drop your CSV here',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _selectedFileName != null 
                                    ? _formatBytes(_selectedFileSize)
                                    : 'or click to browse',
                                style: const TextStyle(color: Colors.grey, fontSize: 14),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Button / Loading / Success State
                    if (_isAnalyzing) ...[
                      const CircularProgressIndicator(color: Color(0xFF00BFA5)),
                      const SizedBox(height: 16),
                      const Text(
                        'Analyzing dataset for fairness patterns...',
                        style: TextStyle(color: Color(0xFF00BFA5), fontSize: 14, fontWeight: FontWeight.w500),
                      ),
                    ] else if (_isSuccess) ...[
                      // Dynamic Insights
                      Row(
                        children: [
                          Expanded(child: _buildInsightCard(
                            'Sensitive Attributes Detected', 
                            _detectedAttributes.isEmpty ? 'None' : _detectedAttributes.map((e) => e[0].toUpperCase() + e.substring(1)).join(', '), 
                            const Color(0xFF00BFA5)
                          )),
                          const SizedBox(width: 12),
                          Expanded(child: _buildInsightCard(
                            'Potential Bias Risk', 
                            _getBiasRiskLevel(_biasScore), 
                            _getBiasRiskColor(_biasScore)
                          )),
                          const SizedBox(width: 12),
                          Expanded(child: _buildInsightCard(
                            'Missing Values', 
                            '${_missingPercentage}%', 
                            Colors.white
                          )),
                        ],
                      ),
                    ] else ...[
                      // Upload Button
                      MouseRegion(
                        onEnter: (_) => setState(() => _isHovering = true),
                        onExit: (_) => setState(() => _isHovering = false),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 280,
                          height: 48,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            boxShadow: _isHovering && _selectedFileName != null
                                ? [
                                    BoxShadow(
                                      color: const Color(0xFF00BFA5).withOpacity(0.4),
                                      blurRadius: 12,
                                      spreadRadius: 2,
                                    )
                                  ]
                                : [],
                          ),
                          child: ElevatedButton(
                            onPressed: _selectedFileName != null ? _processUpload : null,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF00BFA5),
                              foregroundColor: const Color(0xFF0A0A0F),
                              disabledBackgroundColor: const Color(0xFF00BFA5).withOpacity(0.5),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                            child: const Text(
                              'Analyze Dataset',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      if (_selectedFileName == null) ...[
                        const Text(
                          'No dataset loaded',
                          style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                        ),
                      ] else ...[
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.check_circle, color: Color(0xFF00BFA5), size: 18),
                            const SizedBox(width: 8),
                            Text(
                              '$_selectedFileName uploaded successfully',
                              style: const TextStyle(color: Color(0xFF00BFA5), fontWeight: FontWeight.w500),
                            ),
                          ],
                        ),
                      ],
                    ],
                    
                    if (!_isSuccess && !_isAnalyzing && _selectedFileName == null) ...[
                      const SizedBox(height: 32),
                      const Text(
                        'Supported formats: CSV',
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightCard(String title, String value, Color valueColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0F),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white.withOpacity(0.1), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Colors.white38, fontSize: 10, height: 1.2)),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: valueColor, fontSize: 13, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

class _DataVisualizationBackgroundPainter extends CustomPainter {
  final double animationValue;

  _DataVisualizationBackgroundPainter({required this.animationValue});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00BFA5).withOpacity(0.04)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final double spacing = 40.0;
    final double offset = animationValue * spacing;

    for (double i = -size.height; i < size.width; i += spacing) {
      final startX = i + offset;
      final startY = 0.0;
      final endX = startX + size.height;
      final endY = size.height;
      
      canvas.drawLine(Offset(startX, startY), Offset(endX, endY), paint);
    }
  }

  @override
  bool shouldRepaint(covariant _DataVisualizationBackgroundPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}
