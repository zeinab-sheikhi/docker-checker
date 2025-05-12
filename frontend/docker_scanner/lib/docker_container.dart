import 'package:docker_scanner/widgets/my_button.dart';
import 'package:flutter/material.dart';
import 'package:docker_scanner/widgets/my_container.dart';
import 'package:docker_scanner/consts.dart';
import 'package:docker_scanner/providers/job_provider.dart';
import 'package:docker_scanner/widgets/my_row_label.dart';
import 'package:docker_scanner/widgets/my_scrollable_text.dart';
import 'package:provider/provider.dart';
import 'package:flutter/services.dart';
import 'package:docker_scanner/widgets/my_table.dart';
import 'package:docker_scanner/widgets/job_status_summary.dart';

class DockerContainer extends StatefulWidget {
  const DockerContainer({super.key});

  @override
  State<DockerContainer> createState() => _DockerContainerState();
}

class _DockerContainerState extends State<DockerContainer> {
  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);

    // Don't show anything if there's an error or no job data
    if (jobProvider.error != null ||
        jobProvider.statusError != null ||
        (jobProvider.jobIdResponse == null && !jobProvider.isProcessing)) {
      return const SizedBox.shrink();
    }

    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 500),
      switchInCurve: Curves.easeInOut,
      switchOutCurve: Curves.easeInOut,
      transitionBuilder:
          (child, animation) =>
              FadeTransition(opacity: animation, child: child),
      child: _buildContent(jobProvider),
    );
  }

  Widget _buildContent(JobProvider jobProvider) {
    if (jobProvider.jobIdResponse == null) {
      return const SizedBox.shrink();
    }

    return SingleChildScrollView(
      child: Column(
        key: ValueKey('docker_container_${jobProvider.jobIdResponse?.jobId}'),
        children: [
          const SizedBox(height: 32),
          MyContainer(
            backgroundColor: kContainerBackground,
            width: 1000,
            padding: const EdgeInsets.all(20),
            child: _buildJobStatus(jobProvider),
          ),
        ],
      ),
    );
  }

  Widget _buildJobStatus(JobProvider jobProvider) {
    if (jobProvider.isProcessing) {
      return SizedBox(height: 200, child: _circularLoading('Processing...'));
    }

    if (jobProvider.canShowResults) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            height: 300, // Fixed height
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  flex: 3,
                  child: _withActionButtonContainer(
                    'File Content',
                    'Copy',
                    'Copied',
                    jobProvider.isFileContentCopied,
                    () => _copyFileContent(jobProvider),
                    jobProvider.dockerfile,
                  ),
                ),
                const SizedBox(width: 30),
                const Expanded(flex: 2, child: JobStatusSummary()),
              ],
            ),
          ),

          if (jobProvider.canShowVulnerabilities) ...[
            const SizedBox(height: 60),
            MyVulnerabilityTable(
              rows:
                  jobProvider.vulnerabilities!
                      .map(
                        (v) => VulnerabilityRow(
                          library: v.package,
                          vulnerability: v.vulnerabilityId,
                          severity: v.severity,
                          fixedVersion: v.fixedVersion ?? 'N/A',
                          title: v.title ?? '',
                        ),
                      )
                      .toList(),
            ),
          ],
        ],
      );
    }

    return const SizedBox(height: 200);
  }

  Widget _circularLoading(String message) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            width: 64,
            height: 64,
            child: CircularProgressIndicator(
              strokeWidth: 6,
              valueColor: AlwaysStoppedAnimation<Color>(kPrimary),
              backgroundColor: kPrimaryLight,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            message,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 22,
              color: kTextColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _withActionButtonContainer(
    String title,
    String actionButtonText,
    String actionButtonPressedText,
    bool isPressed,
    VoidCallback onPressed,
    String? content, {
    double verticalSpacing = 20,
  }) {
    return Container(
      width: double.infinity,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: double.infinity, // Makes row label take full width
            child: MyRowLabel(
              label: title,
              rightChild: MyButton(
                text: isPressed ? actionButtonPressedText : actionButtonText,
                onPressed: isPressed ? null : onPressed,
                width: 100,
                height: 40,
                fontSize: 18,
              ),
            ),
          ),
          SizedBox(height: verticalSpacing),
          Expanded(
            child: MyContainer(
              width: double.infinity, // Makes container take full width
              padding: const EdgeInsets.all(10),
              borderRadius: 5,
              boxShadowOffset: const Offset(5, 5),
              child:
                  content != null
                      ? MyScrollableText(text: content)
                      : const SizedBox.shrink(),
            ),
          ),
        ],
      ),
    );
  }

  void _copyFileContent(JobProvider jobProvider) async {
    await Clipboard.setData(
      ClipboardData(text: jobProvider.jobStatusResponse?.dockerfile ?? ''),
    );
    jobProvider.setFileContentCopied(true);
    Future.delayed(const Duration(seconds: 2), () {
      jobProvider.setFileContentCopied(false);
    });
  }
}
