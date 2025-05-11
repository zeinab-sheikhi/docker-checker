import 'package:flutter/material.dart';
import '../consts.dart';

class MyScrollableText extends StatelessWidget {
  final String text;
  final double? fontSize;
  final Color? fontColor;
  final EdgeInsetsGeometry padding;

  const MyScrollableText({
    super.key,
    required this.text,
    this.fontSize,
    this.fontColor,
    this.padding = const EdgeInsets.all(18),
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.vertical,
      child: Padding(
        padding: padding,
        child: Text(
          text,
          style: TextStyle(
            fontFamily: 'JetBrainsMono',
            fontSize: fontSize ?? 15,
            color: fontColor ?? const Color(0xFF23272F),
          ),
        ),
      ),
    );
  }
}
