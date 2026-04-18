import 'package:flutter/material.dart';

class UploadDatasetScreen extends StatelessWidget {
  const UploadDatasetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Dataset')),
      body: Center(
        child: Card(
          elevation: 4,
          margin: const EdgeInsets.all(32),
          child: Padding(
            padding: const EdgeInsets.all(48.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.insert_drive_file, size: 64, color: Colors.grey),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    // UI only, no real upload logic
                  },
                  icon: const Icon(Icons.upload),
                  label: const Text('Upload CSV'),
                ),
                const SizedBox(height: 16),
                const Text(
                  'No dataset loaded',
                  style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
