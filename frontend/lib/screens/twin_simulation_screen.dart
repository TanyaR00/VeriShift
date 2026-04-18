import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TwinSimulationScreen extends StatefulWidget {
  const TwinSimulationScreen({super.key});

  @override
  State<TwinSimulationScreen> createState() => _TwinSimulationScreenState();
}

class _TwinSimulationScreenState extends State<TwinSimulationScreen> {
  final _ageController = TextEditingController();
  final _incomeController = TextEditingController();
  final _newValueController = TextEditingController(text: 'male');
  final ScrollController _scrollController = ScrollController();

  String _gender = 'female';
  String _education = 'bachelors';
  String _employment = 'employed';
  String _changedField = 'gender';

  bool _showResults = false;
  Map<String, dynamic>? _explanationResult;

  @override
  void dispose() {
    _ageController.dispose();
    _incomeController.dispose();
    _newValueController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _testAlternateReality() async {
    // Collect data
    final original = {
      'age': int.tryParse(_ageController.text) ?? 30,
      'income': double.tryParse(_incomeController.text) ?? 50000.0,
      'gender': _gender,
      'education': _education,
      'employment_status': _employment,
    };

    final twinInput = {
      'original': original,
      'changed_field': _changedField,
      'changed_value': _newValueController.text,
    };

    // Close keyboard before showing results
    FocusScope.of(context).unfocus();

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/explain'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(twinInput),
      );

      if (response.statusCode == 200) {
        setState(() {
          _explanationResult = jsonDecode(response.body);
          _showResults = true;
        });
        _scrollToResults();
      }
    } catch (e) {
      // Dummy response for UI demonstration
      setState(() {
        _explanationResult = {
          'original_prediction': 0,
          'twin_prediction': 1,
          'original_confidence': 72,
          'twin_confidence': 89,
          'explanation':
              '⚡ $_changedField changed: $_gender → ${_newValueController.text}\n📊 Approval probability increased by 17%\n🔍 Historical patterns show $_changedField bias in training data'
        };
        _showResults = true;
      });
      _scrollToResults();
    }
  }

  void _scrollToResults() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOut,
        );
      }
    });
  }

  InputDecoration _inputDec(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: Colors.grey),
      filled: true,
      fillColor: const Color(0xFF1E1E2E),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: Color(0xFF00BFA5), width: 1.5),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    );
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

  Widget _buildDynamicNewValueField() {
    if (_changedField == 'gender') {
      return DropdownButtonFormField<String>(
        value: _newValueController.text.isEmpty
            ? 'male'
            : _newValueController.text,
        decoration: _inputDec('New Value'),
        dropdownColor: const Color(0xFF1E1E2E),
        items: const [
          DropdownMenuItem(value: 'male', child: Text('Male')),
          DropdownMenuItem(value: 'female', child: Text('Female')),
        ],
        onChanged: (val) {
          if (val != null) _newValueController.text = val;
        },
      );
    } else if (_changedField == 'education') {
      return DropdownButtonFormField<String>(
        value: _newValueController.text.isEmpty
            ? 'bachelors'
            : _newValueController.text,
        decoration: _inputDec('New Value'),
        dropdownColor: const Color(0xFF1E1E2E),
        items: const [
          DropdownMenuItem(value: 'high_school', child: Text('High School')),
          DropdownMenuItem(value: 'bachelors', child: Text('Bachelors')),
          DropdownMenuItem(value: 'masters', child: Text('Masters')),
          DropdownMenuItem(value: 'phd', child: Text('PhD')),
        ],
        onChanged: (val) {
          if (val != null) _newValueController.text = val;
        },
      );
    } else if (_changedField == 'employment_status') {
      return DropdownButtonFormField<String>(
        value: _newValueController.text.isEmpty
            ? 'employed'
            : _newValueController.text,
        decoration: _inputDec('New Value'),
        dropdownColor: const Color(0xFF1E1E2E),
        items: const [
          DropdownMenuItem(value: 'employed', child: Text('Employed')),
          DropdownMenuItem(value: 'unemployed', child: Text('Unemployed')),
          DropdownMenuItem(
              value: 'self_employed', child: Text('Self Employed')),
        ],
        onChanged: (val) {
          if (val != null) _newValueController.text = val;
        },
      );
    } else {
      return TextField(
        controller: _newValueController,
        decoration: _inputDec('New Value'),
        keyboardType: TextInputType.number,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: const [
            Icon(Icons.verified_user, color: Color(0xFF00BFA5)),
            SizedBox(width: 8),
            Text('VeriShift'),
          ],
        ),
      ),
      body: SingleChildScrollView(
        controller: _scrollController,
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader('Original Profile'),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ageController,
                    decoration: _inputDec('Age'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _incomeController,
                    decoration: _inputDec('Income'),
                    keyboardType: TextInputType.number,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _gender,
              decoration: _inputDec('Gender'),
              dropdownColor: const Color(0xFF1E1E2E),
              items: const [
                DropdownMenuItem(value: 'male', child: Text('Male')),
                DropdownMenuItem(value: 'female', child: Text('Female')),
              ],
              onChanged: (val) => setState(() => _gender = val!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _education,
              decoration: _inputDec('Education'),
              dropdownColor: const Color(0xFF1E1E2E),
              items: const [
                DropdownMenuItem(
                    value: 'high_school', child: Text('High School')),
                DropdownMenuItem(value: 'bachelors', child: Text('Bachelors')),
                DropdownMenuItem(value: 'masters', child: Text('Masters')),
                DropdownMenuItem(value: 'phd', child: Text('PhD')),
              ],
              onChanged: (val) => setState(() => _education = val!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _employment,
              decoration: _inputDec('Employment Status'),
              dropdownColor: const Color(0xFF1E1E2E),
              items: const [
                DropdownMenuItem(value: 'employed', child: Text('Employed')),
                DropdownMenuItem(
                    value: 'unemployed', child: Text('Unemployed')),
                DropdownMenuItem(
                    value: 'self_employed', child: Text('Self Employed')),
              ],
              onChanged: (val) => setState(() => _employment = val!),
            ),
            const Divider(height: 48, color: Colors.white10),
            _buildSectionHeader('Alternate Reality (Twin)'),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _changedField,
              decoration: _inputDec('Change field'),
              dropdownColor: const Color(0xFF1E1E2E),
              items: const [
                DropdownMenuItem(value: 'age', child: Text('Age')),
                DropdownMenuItem(value: 'income', child: Text('Income')),
                DropdownMenuItem(value: 'gender', child: Text('Gender')),
                DropdownMenuItem(value: 'education', child: Text('Education')),
                DropdownMenuItem(
                    value: 'employment_status',
                    child: Text('Employment Status')),
              ],
              onChanged: (val) => setState(() {
                _changedField = val!;
                if (val == 'gender')
                  _newValueController.text = 'male';
                else if (val == 'education')
                  _newValueController.text = 'bachelors';
                else if (val == 'employment_status')
                  _newValueController.text = 'employed';
                else
                  _newValueController.text = '';
              }),
            ),
            const SizedBox(height: 16),
            _buildDynamicNewValueField(),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _testAlternateReality,
                child: const Text(
                  'Test Alternate Reality →',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            if (_showResults) ...[
              const SizedBox(height: 32),
              Row(
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF141420),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: Colors.white.withOpacity(0.15), width: 1),
                      ),
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('ORIGINAL',
                              style: TextStyle(
                                  color: Colors.grey,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          Text(
                              _explanationResult?['original_prediction'] == 1
                                  ? 'Approved'
                                  : 'Rejected',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: _explanationResult?[
                                            'original_prediction'] ==
                                        1
                                    ? const Color(0xFF66BB6A)
                                    : const Color(0xFFEF5350),
                              )),
                          const SizedBox(height: 4),
                          AnimatedCounter(
                            value: _explanationResult?['original_confidence'] ??
                                72,
                            suffix: '% confidence',
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF141420),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: Colors.white.withOpacity(0.15), width: 1),
                      ),
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text('TWIN',
                                  style: TextStyle(
                                      color: Colors.grey,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold)),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color:
                                      const Color(0xFF00BFA5).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: const Text('↑ 17% boost',
                                    style: TextStyle(
                                        color: Color(0xFF00BFA5),
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                              _explanationResult?['twin_prediction'] == 1
                                  ? 'Approved'
                                  : 'Rejected',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color:
                                    _explanationResult?['twin_prediction'] == 1
                                        ? const Color(0xFF66BB6A)
                                        : const Color(0xFFEF5350),
                              )),
                          const SizedBox(height: 4),
                          AnimatedCounter(
                            value: _explanationResult?['twin_confidence'] ?? 89,
                            suffix: '% confidence',
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1117),
                  border: const Border(
                      left: BorderSide(color: Color(0xFF00BFA5), width: 4)),
                  borderRadius: const BorderRadius.only(
                      topRight: Radius.circular(8),
                      bottomRight: Radius.circular(8)),
                ),
                child: Text(
                  _explanationResult?['explanation'] ?? '',
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    color: Colors.white,
                    height: 1.6,
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ]
          ],
        ),
      ),
    );
  }
}

class AnimatedCounter extends StatefulWidget {
  final int value;
  final String suffix;

  const AnimatedCounter({super.key, required this.value, required this.suffix});

  @override
  State<AnimatedCounter> createState() => _AnimatedCounterState();
}

class _AnimatedCounterState extends State<AnimatedCounter>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _animation = Tween<double>(begin: 0, end: widget.value.toDouble()).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedCounter oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _animation =
          Tween<double>(begin: 0, end: widget.value.toDouble()).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeOut),
      );
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Text('${_animation.value.toInt()}${widget.suffix}',
            style: const TextStyle(color: Colors.grey, fontSize: 14));
      },
    );
  }
}
