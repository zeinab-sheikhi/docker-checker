class JobResponse {
  final String jobId;
  final String status;
  final double? performance;
  final String? scanReport;
  final List<VulnerabilitySummary>? vulnerabilitySummary;

  JobResponse({
    required this.jobId,
    required this.status,
    this.performance,
    this.scanReport,
    this.vulnerabilitySummary,
  });

  @override
  String toString() {
    return '''
JobResponse {
  id: $jobId,
  status: $status,
  scanReport: $scanReport,
  vulnerabilitySummary: $vulnerabilitySummary
}''';
  }

  factory JobResponse.fromJson(Map<String, dynamic> json) {
    return JobResponse(
      jobId: json['job_id'],
      status: json['status'],
      performance: (json['performance'] as num?)?.toDouble(),
      scanReport: json['scan_report'],
      vulnerabilitySummary:
          (json['vulnerabilities'] as List?)
              ?.map((e) => VulnerabilitySummary.fromJson(e))
              .toList(),
    );
  }
}

class VulnerabilitySummary {
  final String severity;
  final int count;

  VulnerabilitySummary({required this.severity, required this.count});

  factory VulnerabilitySummary.fromJson(Map<String, dynamic> json) {
    return VulnerabilitySummary(
      severity: json['severity'],
      count: json['count'],
    );
  }
}

class JobIdResponse {
  final String jobId;

  JobIdResponse({required this.jobId});

  factory JobIdResponse.fromJson(Map<String, dynamic> json) {
    return JobIdResponse(jobId: json['job_id']);
  }
}
