class VulnerabilitySummary {
  final String package;
  final String vulnerabilityId;
  final String severity;
  final String? title;
  final String? description;
  final String? fixedVersion;

  VulnerabilitySummary({
    required this.package,
    required this.vulnerabilityId,
    required this.severity,
    this.title,
    this.description,
    this.fixedVersion,
  });

  factory VulnerabilitySummary.fromJson(Map<String, dynamic> json) {
    return VulnerabilitySummary(
      package: json['PkgName'] as String,
      vulnerabilityId: json['VulnerabilityID'] as String,
      severity: json['Severity'] as String,
      title: json['Title'] as String?,
      description: json['Description'] as String?,
      fixedVersion: json['FixedVersion'] as String?,
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

enum StepStatus { SUCCESS, FAILED, SKIPPED }

StepStatus stepStatusFromString(String status) {
  return StepStatus.values.firstWhere(
    (e) => e.toString().split('.').last == status.toUpperCase(),
    orElse: () => StepStatus.FAILED,
  );
}

class JobStatusResponse {
  final String jobId;
  final String? dockerfile;

  // Build step
  final StepStatus buildStatus;
  final String? imageId;

  // Scan step
  final StepStatus scanStatus;
  final bool? isSafe;
  final List<VulnerabilitySummary>? vulnerabilities;

  // Run step
  final StepStatus runStatus;
  final double? performance;

  // Single error field
  final String? error;

  JobStatusResponse({
    required this.jobId,
    this.dockerfile,
    required this.buildStatus,
    this.imageId,
    required this.scanStatus,
    this.isSafe,
    this.vulnerabilities,
    required this.runStatus,
    this.performance,
    this.error,
  });

  factory JobStatusResponse.fromJson(Map<String, dynamic> json) {
    return JobStatusResponse(
      jobId: json['job_id'] as String,
      dockerfile: json['dockerfile'] as String?,
      buildStatus: stepStatusFromString(json['build_status'] as String),
      imageId: json['image_id'] as String?,
      scanStatus: stepStatusFromString(json['scan_status'] as String),
      isSafe: json['is_safe'] as bool?,
      vulnerabilities:
          (json['vulnerabilities'] as List?)
              ?.map(
                (e) => VulnerabilitySummary.fromJson(e as Map<String, dynamic>),
              )
              .toList(),
      runStatus: stepStatusFromString(json['run_status'] as String),
      performance: (json['performance'] as num?)?.toDouble(),
      error: json['error'] as String?,
    );
  }

  @override
  String toString() {
    return '''
JobStatusResponse(
  jobId: $jobId,
  buildStatus: $buildStatus,
  imageId: $imageId,
  scanStatus: $scanStatus,
  isSafe: $isSafe,
  vulnerabilities: ${vulnerabilities?.length ?? 0} items,
  runStatus: $runStatus,
  performance: $performance,
  error: $error,
  dockerfile: ${dockerfile != null ? (dockerfile!.length > 40 ? '${dockerfile!.substring(0, 40)}...' : dockerfile) : 'null'}
)''';
  }
}
