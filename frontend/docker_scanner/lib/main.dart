import 'package:docker_scanner/upload_container.dart';
import 'package:flutter/material.dart';
import 'consts.dart';
import 'package:provider/provider.dart';
import 'providers/job_provider.dart';
import 'docker_container.dart';
import 'package:docker_scanner/widgets/my_error_box.dart';

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
        backgroundColor: white,
        appBar: AppBar(
          backgroundColor: kBackgroundColor,
          title: const Row(
            children: [
              Text(
                'Docker',
                style: TextStyle(
                  color: black,
                  fontSize: 24,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                'Scanner',
                style: TextStyle(
                  color: kCriticalSeverity,
                  fontSize: 24,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          elevation: 0,
          toolbarHeight: 100,
          bottom: PreferredSize(
            preferredSize: const Size.fromHeight(2.0),
            child: Container(color: black, height: 4.0),
          ),
        ),
        body: const Padding(
          padding: EdgeInsets.symmetric(vertical: 48),
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
  const DockerScannerPage({super.key});

  @override
  State<DockerScannerPage> createState() => _DockerScannerPageState();
}

class _DockerScannerPageState extends State<DockerScannerPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SizedBox(
          width: 1000,
          child: Column(
            children: [
              Consumer<JobProvider>(
                builder: (context, jobProvider, _) {
                  if (jobProvider.error == null) {
                    return const SizedBox.shrink();
                  }
                  return ErrorMessageBox(message: jobProvider.error!);
                },
              ),
              const Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: [UploadContainer(), DockerContainer()],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
