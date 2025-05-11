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

  static Future<JobResponse> uploadDockerfile(
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
      return JobResponse.fromJson(jsonDecode(response.body));
    } else {
      String errorMsg;
      try {
        final errorJson = jsonDecode(response.body);
        errorMsg = errorJson['detail'] ?? response.body;
      } catch (_) {
        errorMsg = response.body;
      }
      throw ApiException('Failed to upload Dockerfile: $errorMsg');
    }
  }

  static Future<JobIdResponse> submitDockerfile(
    Uint8List fileBytes,
    String filename,
  ) async {
    final uri = Uri.parse('$baseUrl/jobs/');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        await http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: filename,
        ),
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
      throw ApiException('Failed to submit Dockerfile: $errorMsg');
    }
  }
}
