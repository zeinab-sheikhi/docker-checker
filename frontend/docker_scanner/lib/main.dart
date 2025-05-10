import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data';
import 'dart:convert';
import 'widgets/custom_button.dart';
import 'widgets/custom_container.dart';
import 'package:flutter/services.dart'; // For Clipboard

void main() => runApp(DockerScannerApp());

class DockerScannerApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Docker Scanner',
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFFF8F8F5),
        body: Center(
          child: UploadContainer(),
        ),
      ),
    );
  }
}

class UploadContainer extends StatefulWidget {
  @override
  State<UploadContainer> createState() => _UploadContainerState();
}

class _UploadContainerState extends State<UploadContainer> {
  String? _fileContent;
  String? _fileName;
  bool _isProcessing = false;
  bool _showFile = false;
  bool _copied = false;

  Future<void> _pickFile() async {
    setState(() {
      _fileContent = null;
      _fileName = null;
      _showFile = false;
    });
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.any,
      withData: true,
    );
    if (result != null && result.files.single.bytes != null) {
      setState(() {
        _isProcessing = true;
      });
      // Simulate file reading delay for demo (remove in production)
      await Future.delayed(const Duration(milliseconds: 1000));
      Uint8List bytes = result.files.single.bytes!;
      String content = utf8.decode(bytes, allowMalformed: true);
      setState(() {
        _fileContent = content;
        _fileName = result.files.single.name;
        _isProcessing = false;
        _showFile = false; // for animation
      });
      // Fade in the file content
      await Future.delayed(const Duration(milliseconds: 50));
      setState(() {
        _showFile = true;
      });
    }
  }

  void _handleCopy() async {
    Clipboard.setData(ClipboardData(text: _fileContent ?? ''));
    setState(() {
      _copied = true;
    });
    await Future.delayed(const Duration(milliseconds: 1500));
    setState(() {
      _copied = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        CustomContainer(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Expanded(child: SizedBox()), // Placeholder for future input
              CustomButton(
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
          transitionBuilder: (child, animation) => FadeTransition(opacity: animation, child: child),
          child: (_fileContent != null && _showFile)
              ? Column(
                  key: const ValueKey('fileContent'),
                  children: [
                    const SizedBox(height: 32),
                    CustomContainer(
                      backgroundColor: Color(0xFFFAFAFA), // Outer container
                      width: 900,
                      padding: EdgeInsets.all(40),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  _fileName ?? 'Selected File',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                              ),
                              CustomButton(
                                text: _copied ? 'Copied' : 'Copy',
                                onPressed: _copied ? null : _handleCopy,
                                width: 120,
                                height: 44,
                                borderRadius: 8,
                                borderWidth: 3,
                                textColor: Colors.black,
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Container(
                            constraints: const BoxConstraints(maxHeight: 400),
                            width: double.infinity,
                            padding: const EdgeInsets.all(18),
                            decoration: BoxDecoration(
                              color: Color(0xFFFFF4DA), // Updated background
                              borderRadius: BorderRadius.circular(8),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black12,
                                  blurRadius: 4,
                                  offset: Offset(0, 2),
                                ),
                              ],
                            ),
                            child: SingleChildScrollView(
                              scrollDirection: Axis.vertical,
                              child: Text(
                                _fileContent ?? '',
                                style: const TextStyle(
                                  fontFamily: 'JetBrainsMono',
                                  fontSize: 15,
                                  color: Color(0xFF23272F), // Darker text
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                )
              : const SizedBox.shrink(),
        ),
      ],
    );
  }
}