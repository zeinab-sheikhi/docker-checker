import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';

  static Future<Map<String, dynamic>> uploadDockerfile(PlatformFile file) async {
    var uri = Uri.parse('$baseUrl/jobs/');
    var request = http.MultipartRequest('POST', uri);
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        file.bytes!,
        filename: file.name.isNotEmpty ? file.name : 'Dockerfile',
      ),
    );
    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);
    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      return {
        'success': true,
        'scan_report': data['scan_report'] ?? '',
        'performance': data['performance'],
        'status': data['status'],
        'severityCounts': _parseSeverityCounts(data['scan_report'] ?? ''),
      };
    } else {
      String errorMsg = 'Upload failed: ${response.statusCode}';
      try {
        var data = json.decode(response.body);
        errorMsg = data['detail']?.toString() ?? errorMsg;
      } catch (_) {
        errorMsg = response.body;
      }
      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  static Map<String, int> _parseSeverityCounts(String scanReport) {
    // Very basic parsing: count occurrences of severity keywords in the scan report
    final severities = ['Critical', 'High', 'Medium', 'Low'];
    final counts = <String, int>{};
    for (var sev in severities) {
      final regex = RegExp('$sev', caseSensitive: false);
      counts[sev] = regex.allMatches(scanReport).length;
    }
    return counts;
  }

  static Future<String> checkHealth() async {
    final response = await http.get(Uri.parse('$baseUrl/health'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['message'] ?? 'API is running.';
    } else {
      return 'Health check failed: ${response.statusCode}';
    }
  }
} 