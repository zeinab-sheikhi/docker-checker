import 'package:docker_scanner/upload_container.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import 'widgets/my_button.dart';
import 'widgets/my_container.dart';
import 'widgets/my_scrollable_text.dart';
import 'widgets/my_row_label.dart';
import 'widgets/my_donut_chart.dart';
import 'package:flutter/services.dart';
import 'api/api_service.dart';
import 'api/models.dart';
import 'consts.dart';
import 'package:provider/provider.dart';
import 'providers/job_provider.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => JobProvider(),
      child: const DockerScannerApp(),
    ),
  );
}

class DockerScannerApp extends StatelessWidget {
  const DockerScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Docker Scanner',
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: kBackgroundColor,
        body: Padding(
          padding: const EdgeInsets.symmetric(vertical: 48),
          child: Align(
            alignment: Alignment.topCenter,
            child: DockerScannerPage(),
          ),
        ),
      ),
    );
  }
}

class DockerScannerPage extends StatefulWidget {
  @override
  State<DockerScannerPage> createState() => _DockerScannerPageState();
}

class _DockerScannerPageState extends State<DockerScannerPage> {
  String? _fileContent;
  bool _showFile = false;
  bool _fileCopied = false;
  bool _scanCopied = false;
  bool _isLoading = false;
  bool _isProcessing = false;
  JobResponse? _jobResponse;

  Map<String, int> _getSeverityCounts() {
    final summary = _jobResponse?.vulnerabilitySummary;

    if (summary == null) return {};
    return {for (var v in summary) v.severity: v.count};
  }

  Future<void> _pickFile() async {
    setState(() {
      _fileContent = null;
      _isProcessing = false;
      _showFile = false;
      _jobResponse = null;
    });
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.any,
      withData: true,
    );
    if (result != null && result.files.single.bytes != null) {
      setState(() => _isProcessing = true);
      await Future.delayed(const Duration(milliseconds: 1000));
      Uint8List bytes = result.files.single.bytes!;
      String content = utf8.decode(bytes, allowMalformed: true);
      String filename = result.files.single.name;
      setState(() {
        _fileContent = content;
        _isProcessing = false;
        _showFile = false;
      });
      await Future.delayed(const Duration(milliseconds: 50));
      setState(() {
        _showFile = true;
        _isLoading = true;
      });
      // Call the API and show loading
      try {
        final jobResponse = await ApiService.uploadDockerfile(bytes, filename);
        print(jobResponse.toString());
        setState(() => _jobResponse = jobResponse);
      } on ApiException catch (e) {
        // Optionally show error
        // jobProvider.setError(e.message);
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  void _handleFileCopy() async {
    Clipboard.setData(ClipboardData(text: _fileContent ?? ''));
    setState(() => _fileCopied = true);
    await Future.delayed(const Duration(milliseconds: 1500));
    setState(() => _fileCopied = false);
  }

  void _handleScanCopy() async {
    Clipboard.setData(ClipboardData(text: _jobResponse?.scanReport ?? ''));
    setState(() => _scanCopied = true);
    await Future.delayed(const Duration(milliseconds: 1500));
    setState(() => _scanCopied = false);
  }

  Widget buildLoadingContainer() {
    return MyContainer(
      backgroundColor: kContainerBackground,
      width: 900,
      padding: const EdgeInsets.all(40),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
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
              'Loading...',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 22,
                color: kTextColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _fileContentWidget() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        MyRowLabel(
          label: 'File Content',
          rightChild: MyButton(
            text: _fileCopied ? 'Copied' : 'Copy',
            onPressed: _fileCopied ? null : _handleFileCopy,
            width: 100,
            height: 40,
            fontSize: 18,
          ),
        ),
        const SizedBox(height: 10),
        MyContainer(
          borderRadius: 5,
          boxShadowOffset: const Offset(5, 5),
          height: 500,
          width: double.infinity,
          child:
              _fileContent != null
                  ? MyScrollableText(text: _fileContent ?? '')
                  : const SizedBox.shrink(),
        ),
      ],
    );
  }

  Widget _scanSummaryWidget() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 450,
          child: MyRowLabel(
            label: "Scan Summary",
            rightChild: MyButton(
              text: _scanCopied ? 'Copied' : 'Copy',
              onPressed: _scanCopied ? null : _handleScanCopy,
              width: 100,
              height: 40,
              fontSize: 18,
            ),
          ),
        ),
        const SizedBox(height: 10),
        MyContainer(
          borderRadius: 5,
          boxShadowOffset: const Offset(5, 5),
          height: 250,
          width: 450,
          padding: const EdgeInsets.all(5),
          child: MyScrollableText(
            text: _jobResponse?.scanReport ?? '',
            padding: const EdgeInsets.all(10),
          ),
        ),
      ],
    );
  }

  Widget _donutChartWidget(Map<String, int>? data) {
    return data != null
        ? MyDonutChart(severityCounts: data)
        : const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);

    // Your file picking logic here
    // Uint8List? fileBytes;
    // String? filename;

    return SingleChildScrollView(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const UploadContainer(),
          // MyContainer(
          //   width: 900,
          //   child: Row(
          //     mainAxisSize: MainAxisSize.min,
          //     children: [
          //       const Expanded(child: SizedBox()),
          //       MyButton(
          //         text: 'Upload',
          //         onPressed:
          //             jobProvider.isLoading
          //                 ? null
          //                 : () async {
          //                   // Pick the file
          //                   FilePickerResult? result = await FilePicker.platform
          //                       .pickFiles(withData: true);
          //                   if (result != null &&
          //                       result.files.single.bytes != null) {
          //                     final fileBytes = result.files.single.bytes!;
          //                     final filename = result.files.single.name;
          //                     await jobProvider.submitDockerfile(
          //                       fileBytes,
          //                       filename,
          //                     );
          //                   } else {
          //                     // Optionally, you can set an error in the provider or show a message
          //                     jobProvider.error = "No file selected.";
          //                     jobProvider.notifyListeners();
          //                   }
          //                 },
          //         isLoading: jobProvider.isLoading,
          //         loadingText: 'Processing...',
          //       ),
          //     ],
          //   ),
          // ),
          // if (jobProvider.jobIdResponse != null)
          //   Padding(
          //     padding: const EdgeInsets.only(top: 16),
          //     child: Text(
          //       'Job ID: ${jobProvider.jobIdResponse!.jobId}',
          //       style: TextStyle(fontWeight: FontWeight.bold),
          //     ),
          //   )
          // else if (jobProvider.error != null)
          //   Padding(
          //     padding: const EdgeInsets.only(top: 16),
          //     child: Text(
          //       'Error: ${jobProvider.error}',
          //       style: TextStyle(color: Colors.red),
          //     ),
          //   ),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 500),
            switchInCurve: Curves.easeInOut,
            switchOutCurve: Curves.easeInOut,
            transitionBuilder:
                (child, animation) =>
                    FadeTransition(opacity: animation, child: child),
            child:
                (_isLoading ||
                        _jobResponse != null ||
                        (_fileContent != null && _showFile))
                    ? Column(
                      key: const ValueKey('fileContent'),
                      children: [
                        const SizedBox(height: 32),
                        if (_isLoading)
                          buildLoadingContainer()
                        else if (!_isLoading &&
                            (_jobResponse != null ||
                                (_fileContent != null && _showFile)))
                          MyContainer(
                            width: 900,
                            padding: const EdgeInsets.all(32),
                            backgroundColor: kContainerBackground,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Row(
                                //   mainAxisAlignment:
                                //       MainAxisAlignment.spaceBetween,
                                //   children: [
                                //     _scanSummaryWidget(),
                                //     // _donutChartWidget(_getSeverityCounts()),
                                //   ],
                                // ),
                                const SizedBox(height: 32),
                                // --- File Content Section ---
                                _fileContentWidget(),
                              ],
                            ),
                          ),
                      ],
                    )
                    : const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }
}
