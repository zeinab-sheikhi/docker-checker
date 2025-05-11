import 'package:flutter/material.dart';
import 'package:docker_scanner/consts.dart';
import 'package:auto_size_text/auto_size_text.dart';

class ErrorMessageBox extends StatelessWidget {
  final String message;

  const ErrorMessageBox({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 32, bottom: 16),
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 28),
      decoration: BoxDecoration(
        color: kErrorBoxBackground,
        border: Border.all(color: kErrorBoxBorder, width: 2),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.error_outline, color: kErrorBoxText, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: AutoSizeText(
              message,
              style: const TextStyle(
                color: kErrorBoxText,
                fontWeight: FontWeight.w600,
                fontSize: 20,
              ),
              maxLines: 1,
              minFontSize: 12,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
