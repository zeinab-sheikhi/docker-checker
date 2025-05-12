import 'package:flutter/material.dart';
import '../consts.dart';

class JobIdTextFormField extends StatefulWidget {
  final TextEditingController controller;
  final String? hintText;
  final void Function(String)? onChanged;

  const JobIdTextFormField({
    super.key,
    required this.controller,
    this.hintText = 'Enter Job ID',
    this.onChanged,
  });

  @override
  State<JobIdTextFormField> createState() => _JobIdTextFormFieldState();
}

class _JobIdTextFormFieldState extends State<JobIdTextFormField> {
  // UUID v4 regex
  static final _uuidRegExp = RegExp(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
  );

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 0),
      child: Container(
        decoration: BoxDecoration(
          color: kContainerBackground,
          borderRadius: BorderRadius.circular(8),
          border: const Border(
            top: BorderSide(color: kButtonBorder, width: 3),
            left: BorderSide(color: kButtonBorder, width: 3),
            right: BorderSide(color: kButtonBorder, width: 7),
            bottom: BorderSide(color: kButtonBorder, width: 7),
          ),
        ),
        child: TextFormField(
          controller: widget.controller,
          decoration: InputDecoration(
            hintText: widget.hintText,
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
          onChanged: widget.onChanged,
          // validator: (value) {
          //   if (value == null || value.isEmpty) {
          //     return null;
          //   }
          //   if (!_uuidRegExp.hasMatch(value.trim())) {
          //     return 'Please enter a valid UUID (Job ID)';
          //   }
          //   return null;
          // },
          autovalidateMode: AutovalidateMode.disabled,
        ),
      ),
    );
  }
}
