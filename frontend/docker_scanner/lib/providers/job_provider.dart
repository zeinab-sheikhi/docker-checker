import '../api/api_service.dart';
import '../api/models.dart';
import 'package:flutter/foundation.dart';

class JobProvider with ChangeNotifier {
  JobIdResponse? jobIdResponse;
  JobResponse? jobResponse;
  String? error;
  bool isLoading = false;

  // Submit Dockerfile and get job ID
  Future<void> submitDockerfile(Uint8List fileBytes, String filename) async {
    isLoading = true;
    error = null;
    notifyListeners();
    try {
      jobIdResponse = await ApiService.submitDockerfile(fileBytes, filename);
      await Future.delayed(const Duration(seconds: 2));
    } catch (e) {
      error = e.toString();
    }
    isLoading = false;
    notifyListeners();
  }

  void setError(String message) {
    error = message;
    notifyListeners();
  }

  // Upload Dockerfile and get scan result (JobResponse)
  Future<void> scanDockerfile(Uint8List fileBytes, String filename) async {
    isLoading = true;
    error = null;
    notifyListeners();
    try {
      jobResponse = await ApiService.uploadDockerfile(fileBytes, filename);
    } catch (e) {
      error = e.toString();
    }
    isLoading = false;
    notifyListeners();
  }

  // Optionally, add a method to reset state
  void reset() {
    jobIdResponse = null;
    jobResponse = null;
    error = null;
    isLoading = false;
    notifyListeners();
  }
}
