import 'package:flutter/material.dart';

import '../api/api_service.dart';
import '../api/models.dart';
import 'package:flutter/foundation.dart';

class JobProvider with ChangeNotifier {
  JobIdResponse? jobIdResponse;
  JobResponse? jobResponse;
  String? error;
  bool isLoading = false;
  final TextEditingController jobIdController = TextEditingController();

  // Submit Dockerfile and get job ID
  Future<void> submitDockerfile(Uint8List fileBytes, String filename) async {
    isLoading = true;
    error = null;
    jobIdResponse = null;
    notifyListeners();
    try {
      jobIdResponse = await ApiService.submitDockerfile(fileBytes, filename);
      await Future.delayed(
        const Duration(seconds: 2),
      ); // added for nice transition
      jobIdController.text = jobIdResponse!.jobId;
    } catch (e) {
      error = e.toString();
    }
    isLoading = false;
    notifyListeners();
  }

  void setError(String message) {
    error = message;
    jobIdResponse = null;
    notifyListeners();
  }

  @override
  void dispose() {
    jobIdController.dispose();
    super.dispose();
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
