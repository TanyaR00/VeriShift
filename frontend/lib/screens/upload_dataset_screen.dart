import 'package:flutter/material.dart';

class UploadDatasetScreen extends StatelessWidget {
  const UploadDatasetScreen({super.key});

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
      body: Center(
        child: Container(
          margin: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: const Color(0xFF141420),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white.withOpacity(0.15), width: 1),
          ),
          padding: const EdgeInsets.all(48.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 24),
                decoration: BoxDecoration(
                  color: const Color(0xFF0A0A0F),
                  borderRadius: BorderRadius.circular(8),
                  // Dashed border simulated using a regular semi-transparent border
                  border: Border.all(color: Colors.white.withOpacity(0.15), width: 1),
                ),
                child: Column(
                  children: const [
                    Icon(Icons.upload_file, size: 48, color: Color(0xFF00BFA5)),
                    SizedBox(height: 16),
                    Text(
                      'Drop your CSV here',
                      style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'or click to browse',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () {
                    // UI only, no real upload logic
                  },
                  child: const Text('Upload CSV', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'No dataset loaded',
                style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
              ),
              const SizedBox(height: 32),
              const Text(
                'Supported formats: CSV, JSON',
                style: TextStyle(color: Colors.grey, fontSize: 10),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
