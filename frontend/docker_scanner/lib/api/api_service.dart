import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'models.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';

  static Future<JobIdResponse> createJob(
    Uint8List fileBytes,
    String filename,
  ) async {
    final uri = Uri.parse('$baseUrl/jobs/');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes('file', fileBytes, filename: filename),
      );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return JobIdResponse.fromJson(jsonDecode(response.body));
    } else {
      String errorMsg;
      try {
        final errorJson = jsonDecode(response.body);
        errorMsg = errorJson['detail'] ?? errorJson['error'] ?? response.body;
      } catch (_) {
        errorMsg = response.body;
      }
      throw ApiException(errorMsg);
    }
  }

  static Future<JobStatusResponse> getJobStatus(String jobId) async {
    final uri = Uri.parse('$baseUrl/jobs/status/$jobId');
    final response = await http.get(uri);
    print(response.body);

    if (response.statusCode == 200) {
      return JobStatusResponse.fromJson(jsonDecode(response.body));
    } else {
      String errorMsg;
      try {
        final errorJson = jsonDecode(response.body);
        errorMsg = errorJson['detail'] ?? errorJson['error'] ?? response.body;
      } catch (_) {
        errorMsg = response.body;
      }
      throw ApiException(errorMsg);
    }
  }
}
