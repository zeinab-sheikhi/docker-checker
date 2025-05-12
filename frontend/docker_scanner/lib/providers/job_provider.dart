import 'package:flutter/material.dart';
import 'dart:async';

import '../api/api_service.dart';
import '../api/models.dart';
import 'package:flutter/foundation.dart';

class JobProvider with ChangeNotifier {
  JobIdResponse? jobIdResponse;
  JobStatusResponse? jobStatusResponse;
  String? error;
  bool isLoading = false;
  bool isFileContentCopied = false;
  final TextEditingController jobIdController = TextEditingController();

  // Submit Dockerfile and get job ID
  Future<void> createJob(Uint8List fileBytes, String filename) async {
    isLoading = true;
    error = null;
    jobIdResponse = null;
    jobStatusResponse = null;
    isFileContentCopied = false;
    notifyListeners();

    try {
      jobIdResponse = await ApiService.createJob(fileBytes, filename);
      jobIdController.text = jobIdResponse!.jobId;
      // Get job status
      Future.delayed(const Duration(seconds: 2));
      await getJobStatus(jobIdResponse!.jobId);
    } catch (e) {
      error = e.toString();
      notifyListeners();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  // Get job status
  Future<void> getJobStatus(String jobId) async {
    try {
      final status = await ApiService.getJobStatus(jobId);
      jobStatusResponse = status;
      // Set the error from JobStatusResponse if it exists
      error =
          status.error; // This will set error to null if status.error is null
      notifyListeners();
    } catch (e) {
      error = e.toString();
      notifyListeners();
    }
  }

  // Step Status Getters
  StepStatus get buildStatus =>
      jobStatusResponse?.buildStatus ?? StepStatus.SKIPPED;
  StepStatus get scanStatus =>
      jobStatusResponse?.scanStatus ?? StepStatus.SKIPPED;
  StepStatus get runStatus =>
      jobStatusResponse?.runStatus ?? StepStatus.SKIPPED;

  // Step Success Checks
  bool get isBuildSuccessful => buildStatus == StepStatus.SUCCESS;
  bool get isScanSuccessful => scanStatus == StepStatus.SUCCESS;
  bool get isRunSuccessful => runStatus == StepStatus.SUCCESS;

  // Step Failure Checks
  bool get hasBuildFailed => buildStatus == StepStatus.FAILED;
  bool get hasScanFailed => scanStatus == StepStatus.FAILED;
  bool get hasRunFailed => runStatus == StepStatus.FAILED;

  // Step Skip Checks
  bool get isBuildSkipped => buildStatus == StepStatus.SKIPPED;
  bool get isScanSkipped => scanStatus == StepStatus.SKIPPED;
  bool get isRunSkipped => runStatus == StepStatus.SKIPPED;

  // Result Getters
  String? get imageId => jobStatusResponse?.imageId;
  bool? get isImageSafe => jobStatusResponse?.isSafe;
  List<VulnerabilitySummary>? get vulnerabilities =>
      jobStatusResponse?.vulnerabilities;
  double? get performance => jobStatusResponse?.performance;
  String? get dockerfile => jobStatusResponse?.dockerfile;
  String? get statusError => jobStatusResponse?.error;

  // Combined Status Checks
  bool get isProcessing => isLoading;

  bool get hasError => statusError != null;

  bool get canShowResults =>
      !isProcessing && !hasError && isBuildSuccessful && isScanSuccessful;

  bool get canShowVulnerabilities =>
      canShowResults && vulnerabilities != null && vulnerabilities!.isNotEmpty;

  bool get canShowPerformance =>
      canShowResults && isRunSuccessful && performance != null;

  bool get isContainerRunning =>
      jobStatusResponse?.performance != null &&
      jobStatusResponse?.error == null;

  void setError(String message) {
    error = message;
    jobIdResponse = null;
    jobStatusResponse = null;
    notifyListeners();
  }

  void setFileContentCopied(bool value) {
    isFileContentCopied = value;
    notifyListeners();
  }

  @override
  void dispose() {
    jobIdController.dispose();
    super.dispose();
  }

  // Reset state
  void reset() {
    jobIdResponse = null;
    jobStatusResponse = null;
    error = null;
    isLoading = false;
    isFileContentCopied = false;
    notifyListeners();
  }
}
