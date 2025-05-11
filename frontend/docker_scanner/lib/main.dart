import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import 'widgets/my_button.dart';
import 'widgets/my_container.dart';
import 'widgets/my_scrollable_text.dart';
import 'widgets/my_row_label.dart';
import 'widgets/my_ring_chart.dart';
import 'package:flutter/services.dart';
import 'api/api_service.dart';
import 'api/models.dart';
import 'consts.dart';

void main() => runApp(DockerScannerApp());

class DockerScannerApp extends StatelessWidget {
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
            child: UploadContainer(),
          ),
        ),
      ),
    );
  }
}

class UploadContainer extends StatefulWidget {
  @override
  State<UploadContainer> createState() => _UploadContainerState();
}

final dummyData = {'Critical': 40, 'High': 15, 'Medium': 15, 'Low': 30};

class _UploadContainerState extends State<UploadContainer> {
  String? _fileContent;
  String? _fileName;
  bool _isProcessing = false;
  bool _showFile = false;
  bool _copied = false;
  bool _isLoading = false;
  JobResponse? _jobResponse;

  Map<String, int> _getSeverityCounts() {
    final summary = _jobResponse?.vulnerabilitySummary;
    if (summary == null) return {};
    return {for (var v in summary) v.severity: v.count};
  }

  Future<void> _pickFile() async {
    setState(() {
      _fileContent = null;
      _fileName = null;
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
        _fileName = filename;
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
        setState(() => _jobResponse = jobResponse);
      } on ApiException catch (e) {
        // Optionally show error
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  void _handleCopy() async {
    Clipboard.setData(ClipboardData(text: _fileContent ?? ''));
    setState(() => _copied = true);
    await Future.delayed(const Duration(milliseconds: 1500));
    setState(() => _copied = false);
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

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          MyContainer(
            width: 900,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Expanded(child: SizedBox()),
                MyButton(
                  text: 'Upload',
                  onPressed: _pickFile,
                  isProcessing: _isProcessing,
                  processingText: 'Processing...',
                ),
              ],
            ),
          ),
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
                                // --- Scan Summary Section ---
                                MyContainer(
                                  borderRadius: 5,
                                  boxShadowOffset: const Offset(5, 5),
                                  height: 250,
                                  width: 450,
                                  child: MyScrollableText(
                                    text: _jobResponse?.scanReport ?? '',
                                  ),
                                ),
                                MyRingChart(severityCounts: dummyData),
                                const SizedBox(height: 32),
                                // --- File Content Section ---
                                MyRowLabel(
                                  label: 'File Content',
                                  rightChild: MyButton(
                                    text: _copied ? 'Copied' : 'Copy',
                                    onPressed: _copied ? null : _handleCopy,
                                    width: 120,
                                    height: 44,
                                    borderRadius: 8,
                                    borderWidth: 3,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                MyContainer(
                                  borderRadius: 5,
                                  boxShadowOffset: const Offset(5, 5),
                                  height: 500,
                                  child:
                                      _fileContent != null
                                          ? MyScrollableText(
                                            text: _fileContent ?? '',
                                          )
                                          : const SizedBox.shrink(),
                                ),
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
