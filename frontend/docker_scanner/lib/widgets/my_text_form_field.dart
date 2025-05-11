import 'package:flutter/material.dart';
import '../consts.dart';

class JobIdTextFormField extends StatelessWidget {
  final TextEditingController controller;
  final String? hintText;
  final void Function(String)? onChanged;

  const JobIdTextFormField({
    super.key,
    required this.controller,
    this.hintText = 'Enter Job ID',
    this.onChanged,
  });

  // UUID v4 regex
  static final _uuidRegExp = RegExp(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
  );

  String? _uuidValidator(String? value) {
    if (value == null || value.isEmpty) {
      return null;
    }
    if (!_uuidRegExp.hasMatch(value.trim())) {
      return 'Please enter a valid UUID (Job ID)';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 0),
      child: Container(
        decoration: BoxDecoration(
          color: kContainerBackground,
          borderRadius: BorderRadius.circular(10),
          border: const Border(
            top: BorderSide(color: kButtonBorder, width: 3),
            left: BorderSide(color: kButtonBorder, width: 3),
            right: BorderSide(color: kButtonBorder, width: 7), // Thicker right
            bottom: BorderSide(
              color: kButtonBorder,
              width: 7,
            ), // Thicker bottom
          ),
        ),
        child: TextFormField(
          controller: controller,
          decoration: InputDecoration(
            hintText: hintText,
            errorText: null,
            hintStyle: TextStyle(
              color: kTextColor.withAlpha((255 * 0.6).round()),
              fontSize: 22,
              fontWeight: FontWeight.w500,
            ),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(
              vertical: 16,
              horizontal: 18,
            ),
          ),
          style: const TextStyle(
            color: kTextColor,
            fontSize: 22,
            fontWeight: FontWeight.w500,
          ),
          validator: _uuidValidator,
          onChanged: onChanged,
          autovalidateMode: AutovalidateMode.onUserInteraction,
        ),
      ),
    );
  }
}
