import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://verishift.onrender.com';

  static Future<Map<String, dynamic>> predict({
    required int age,
    required double income,
    required String gender,
    required String education,
    required String employmentStatus,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predict'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'age': age,
        'income': income,
        'gender': gender,
        'education': education,
        'employment_status': employmentStatus,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Predict failed: ${response.body}');
  }

  static Future<Map<String, dynamic>> createTwin({
    required int age,
    required double income,
    required String gender,
    required String education,
    required String employmentStatus,
    required String changedField,
    required String changedValue,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/create-twin'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'original': {
          'age': age,
          'income': income,
          'gender': gender,
          'education': education,
          'employment_status': employmentStatus,
        },
        'changed_field': changedField,
        'changed_value': changedValue,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Create twin failed: ${response.body}');
  }
}
