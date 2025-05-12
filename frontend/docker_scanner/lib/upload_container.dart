import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import 'package:docker_scanner/providers/job_provider.dart';
import 'package:docker_scanner/widgets/my_container.dart';
import 'package:docker_scanner/widgets/my_button.dart';
import 'package:docker_scanner/widgets/my_text_form_field.dart';

class UploadContainer extends StatefulWidget {
  const UploadContainer({super.key});

  @override
  State<UploadContainer> createState() => _UploadContainerState();
}

class _UploadContainerState extends State<UploadContainer> {
  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);
    return MyContainer(
      width: 1000,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Expanded(flex: 3, child: _jobIdTextFormField(jobProvider)),
          const SizedBox(width: 32),
          Expanded(flex: 1, child: _uploadButton(jobProvider)),
        ],
      ),
    );
  }
}

Widget _uploadButton(JobProvider jobProvider) {
  return MyButton(
    text: 'Upload',
    isLoading: jobProvider.isLoading,
    loadingText: 'Processing...',
    onPressed:
        jobProvider.isLoading
            ? null // the button must be disabled when it is calling the API
            : () async {
              jobProvider.jobIdController.clear();
              // Pick the file
              final picked = await _pickFile();
              if (picked.fileBytes != null && picked.filename != null) {
                await jobProvider.createJob(
                  picked.fileBytes!,
                  picked.filename!,
                );
              } else {
                jobProvider.setError(picked.error ?? "Unknown error.");
              }
            },
  );
}

Widget _jobIdTextFormField(JobProvider jobProvider) {
  return JobIdTextFormField(
    controller: jobProvider.jobIdController,
    hintText: 'Enter Job ID',
    onChanged: (value) {
      jobProvider.jobIdController.text = value;
    },
  );
}

Future<({Uint8List? fileBytes, String? filename, String? error})>
_pickFile() async {
  try {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      withData: true,
    );
    if (result != null && result.files.single.bytes != null) {
      final fileBytes = result.files.single.bytes!;
      final filename = result.files.single.name;
      return (fileBytes: fileBytes, filename: filename, error: null);
    }
    return (fileBytes: null, filename: null, error: "No file selected.");
  } catch (e) {
    return (fileBytes: null, filename: null, error: "Error picking file: $e");
  }
}
