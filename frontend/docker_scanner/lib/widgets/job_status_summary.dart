import 'package:docker_scanner/widgets/my_container.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:docker_scanner/providers/job_provider.dart';
import 'package:docker_scanner/consts.dart';

class JobStatusSummary extends StatelessWidget {
  const JobStatusSummary({super.key});

  Widget _buildStatusItem(IconData icon, Color iconColor, String text) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, color: iconColor, size: 40),
        const SizedBox(height: 8),
        Text(
          text,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final jobProvider = context.watch<JobProvider>();
    final jobStatus = jobProvider.jobStatusResponse;
    Color _successColor = kLowSeverity;
    Color _warningColor = kMediumSeverity;
    Color _errorColor = kCriticalSeverity;

    if (jobStatus == null) return const SizedBox.shrink();

    return MyContainer(
      // padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          // Build Status
          _buildStatusItem(
            jobProvider.isBuildSuccessful ? Icons.check_circle : Icons.error,
            jobProvider.isBuildSuccessful ? _successColor : _errorColor,
            jobProvider.isBuildSuccessful
                ? 'Image built successfully'
                : 'Build failed: ${jobStatus.error}',
          ),
          const Divider(color: Colors.transparent),

          // Scan Status
          if (jobProvider.isBuildSuccessful)
            _buildStatusItem(
              jobProvider.isScanSuccessful
                  ? ((jobProvider.isImageSafe ?? false)
                      ? Icons.check_circle
                      : Icons.warning)
                  : Icons.error,
              jobProvider.isScanSuccessful
                  ? ((jobProvider.isImageSafe ?? false)
                      ? _successColor
                      : _warningColor)
                  : _errorColor,
              jobProvider.isScanSuccessful
                  ? ((jobProvider.isImageSafe ?? false)
                      ? 'Image is Safe'
                      : 'Scan found ${jobStatus.vulnerabilities?.length ?? 0} vulnerabilities in image')
                  : 'Scan failed: ${jobStatus.error}',
            ),
          const Divider(color: Colors.transparent),

          // Container Run Status
          if (jobProvider.isScanSuccessful)
            _buildStatusItem(
              !(jobProvider.isImageSafe ?? false)
                  ? Icons.error
                  : (jobStatus.error != null
                      ? Icons.error
                      : Icons.check_circle),
              !(jobProvider.isImageSafe ?? false)
                  ? _errorColor
                  : (jobStatus.error != null ? _errorColor : _successColor),
              !(jobProvider.isImageSafe ?? false)
                  ? 'Container did not run, Image Not Safe'
                  : (jobStatus.error != null
                      ? 'Container Failed to Run: ${jobStatus.error}'
                      : 'Container Running, Performance: ${jobStatus.performance ?? "N/A"}'),
            ),
        ],
      ),
    );
  }
}
