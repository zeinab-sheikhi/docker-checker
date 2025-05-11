import 'package:flutter/material.dart';
import '../consts.dart';

class MyButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final String loadingText;
  final Widget? icon;
  final Color backgroundColor;
  final Color textColor;
  final Color borderColor;
  final double borderRadius;
  final double borderWidth;
  final Color loaderColor;
  final double width;
  final double height;
  final double fontSize;

  const MyButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.loadingText = 'Processing...',
    this.icon,
    this.backgroundColor = kPrimary,
    this.textColor = kTextColor,
    this.borderColor = kButtonBorder,
    this.borderRadius = 8,
    this.borderWidth = 4,
    this.loaderColor = kTextColor,
    this.width = 220,
    this.height = 60,
    this.fontSize = 20,
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
            textStyle: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: fontSize,
            ),
            padding: EdgeInsets.zero,
          ),
          onPressed: isLoading ? null : onPressed,
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            transitionBuilder:
                (child, animation) =>
                    FadeTransition(opacity: animation, child: child),
            child:
                isLoading
                    ? Row(
                      key: const ValueKey('processing'),
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 3,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              loaderColor,
                            ),
                            backgroundColor: Colors.transparent,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          loadingText,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: textColor,
                          ),
                        ),
                      ],
                    )
                    : Row(
                      key: const ValueKey('upload'),
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (icon != null) ...[icon!, const SizedBox(width: 8)],
                        Text(
                          text,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: textColor,
                          ),
                        ),
                      ],
                    ),
          ),
        ),
      ),
    );
  }
}
