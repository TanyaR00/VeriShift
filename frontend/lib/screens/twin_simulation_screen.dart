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
  final _newValueController = TextEditingController();

  String _gender = 'female';
  String _education = 'bachelors';
  String _employment = 'employed';
  String _changedField = 'gender';

  bool _showResults = false;
  Map<String, dynamic>? _explanationResult;

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
      }
    } catch (e) {
      // In a real app we'd show an error snackbar
      print('Error calling API: $e');
      
      // Fallback for UI demonstration if backend isn't running
      setState(() {
        _explanationResult = {
          'original_prediction': 0,
          'twin_prediction': 1,
          'explanation': 'Dummy text: Changing $_changedField increased approval probability based on historical patterns.'
        };
        _showResults = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Twin Simulation')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Original Profile', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ageController,
                    decoration: const InputDecoration(labelText: 'Age', border: OutlineInputBorder()),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _incomeController,
                    decoration: const InputDecoration(labelText: 'Income', border: OutlineInputBorder()),
                    keyboardType: TextInputType.number,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _gender,
              decoration: const InputDecoration(labelText: 'Gender', border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'male', child: Text('Male')),
                DropdownMenuItem(value: 'female', child: Text('Female')),
              ],
              onChanged: (val) => setState(() => _gender = val!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _education,
              decoration: const InputDecoration(labelText: 'Education', border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'high_school', child: Text('High School')),
                DropdownMenuItem(value: 'bachelors', child: Text('Bachelors')),
                DropdownMenuItem(value: 'masters', child: Text('Masters')),
                DropdownMenuItem(value: 'phd', child: Text('PhD')),
              ],
              onChanged: (val) => setState(() => _education = val!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _employment,
              decoration: const InputDecoration(labelText: 'Employment Status', border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'employed', child: Text('Employed')),
                DropdownMenuItem(value: 'unemployed', child: Text('Unemployed')),
                DropdownMenuItem(value: 'self_employed', child: Text('Self Employed')),
              ],
              onChanged: (val) => setState(() => _employment = val!),
            ),
            
            const Divider(height: 48),
            
            const Text('Alternate Reality (Twin)', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _changedField,
              decoration: const InputDecoration(labelText: 'Change field', border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'age', child: Text('Age')),
                DropdownMenuItem(value: 'income', child: Text('Income')),
                DropdownMenuItem(value: 'gender', child: Text('Gender')),
                DropdownMenuItem(value: 'education', child: Text('Education')),
                DropdownMenuItem(value: 'employment_status', child: Text('Employment Status')),
              ],
              onChanged: (val) => setState(() => _changedField = val!),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _newValueController,
              decoration: const InputDecoration(labelText: 'New Value', border: OutlineInputBorder()),
            ),
            
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _testAlternateReality,
                style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16)),
                child: const Text('Test Alternate Reality', style: TextStyle(fontSize: 16)),
              ),
            ),
            
            if (_showResults) ...[
              const SizedBox(height: 32),
              const Text('Results', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: Card(
                      color: _explanationResult?['original_prediction'] == 1 ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            const Text('Original', style: TextStyle(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 8),
                            Text(
                              _explanationResult?['original_prediction'] == 1 ? 'Approved' : 'Rejected',
                              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)
                            ),
                            const Text('Confidence: 85%'), // Dummy
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Card(
                      color: _explanationResult?['twin_prediction'] == 1 ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            const Text('Twin', style: TextStyle(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 8),
                            Text(
                              _explanationResult?['twin_prediction'] == 1 ? 'Approved' : 'Rejected',
                              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)
                            ),
                            const Text('Confidence: 75%'), // Dummy
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Colors.blue),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(_explanationResult?['explanation'] ?? ''),
                    ),
                  ],
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
