class UserModel {
  final String userCode;
  final String fullName;
  final String email;
  final String phoneMasked;
  final String demoAadhaarId;
  final String role; // 'USER' or 'INSTITUTION'
  final String? institutionName;

  const UserModel({
    required this.userCode,
    required this.fullName,
    required this.email,
    required this.phoneMasked,
    required this.demoAadhaarId,
    this.role = 'USER',
    this.institutionName,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      userCode: json['user_code'] ?? '',
      fullName: json['full_name'] ?? '',
      email: json['email'] ?? '',
      phoneMasked: json['phone_masked'] ?? '',
      demoAadhaarId: json['demo_aadhaar_id'] ?? 'DEMO-KS-882190',
      role: json['role'] ?? 'USER',
      institutionName: json['institution_name'],
    );
  }

  Map<String, dynamic> toJson() => {
    'user_code': userCode,
    'full_name': fullName,
    'email': email,
    'phone_masked': phoneMasked,
    'demo_aadhaar_id': demoAadhaarId,
    'role': role,
    if (institutionName != null) 'institution_name': institutionName,
  };
}
