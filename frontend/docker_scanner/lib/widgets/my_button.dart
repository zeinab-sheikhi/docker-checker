import 'package:flutter/material.dart';

class MyButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isProcessing;
  final String processingText;
  final Widget? icon;
  final Color backgroundColor;
  final Color textColor;
  final Color borderColor;
  final double borderRadius;
  final double borderWidth;
  final Color loaderColor;
  final double width;
  final double height;

  const MyButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isProcessing = false,
    this.processingText = 'Processing...',
    this.icon,
    this.backgroundColor = const Color(0xFFFFC480),
    this.textColor = Colors.black,
    this.borderColor = Colors.black,
    this.borderRadius = 8,
    this.borderWidth = 4,
    this.loaderColor = const Color(0xFF444444),
    this.width = 220,
    this.height = 60,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Material(
        elevation: 8,
        borderRadius: BorderRadius.circular(borderRadius),
        child: OutlinedButton(
          style: OutlinedButton.styleFrom(
            backgroundColor: backgroundColor,
            foregroundColor: textColor,
            side: BorderSide(color: borderColor, width: borderWidth),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(borderRadius),
            ),
            textStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
            padding: EdgeInsets.zero,
          ),
          onPressed: isProcessing ? null : onPressed,
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            transitionBuilder: (child, animation) => FadeTransition(opacity: animation, child: child),
            child: isProcessing
                ? Row(
                    key: const ValueKey('processing'),
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 3,
                          valueColor: AlwaysStoppedAnimation<Color>(loaderColor),
                          backgroundColor: Colors.transparent,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        processingText,
                        style: TextStyle(fontWeight: FontWeight.bold, color: textColor),
                      ),
                    ],
                  )
                : Row(
                    key: const ValueKey('upload'),
                    mainAxisAlignment: MainAxisAlignment.center,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (icon != null) ...[
                        icon!,
                        const SizedBox(width: 8),
                      ],
                      Text(
                        text,
                        style: TextStyle(fontWeight: FontWeight.bold, color: textColor),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
