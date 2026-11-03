class UserModel {
  final String userCode;
  final String fullName;
  final String email;
  final String phoneMasked;

  const UserModel({
    required this.userCode,
    required this.fullName,
    required this.email,
    required this.phoneMasked,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      userCode: json['user_code'] ?? '',
      fullName: json['full_name'] ?? '',
      email: json['email'] ?? '',
      phoneMasked: json['phone_masked'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'user_code': userCode,
    'full_name': fullName,
    'email': email,
    'phone_masked': phoneMasked,
  };
}

