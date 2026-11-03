class CredentialModel {
  final String id;
  final String category;
  final String title;
  final String issuer;
  final String status;
  final String issueDate;
  final String expiryDate;
  final bool isSynthetic;
  final String? verificationHash;
  final Map<String, dynamic>? safeAttributes;
  final String? privacyNotice;

  const CredentialModel({
    required this.id,
    required this.category,
    required this.title,
    required this.issuer,
    required this.status,
    required this.issueDate,
    required this.expiryDate,
    required this.isSynthetic,
    this.verificationHash,
    this.safeAttributes,
    this.privacyNotice,
  });

  factory CredentialModel.fromJson(Map<String, dynamic> json) {
    return CredentialModel(
      id: json['id'] ?? '',
      category: json['category'] ?? '',
      title: json['title'] ?? '',
      issuer: json['issuer'] ?? 'KavachSetu Demo Issuer',
      status: json['status'] ?? 'VALID',
      issueDate: json['issue_date'] ?? '',
      expiryDate: json['expiry_date'] ?? '',
      isSynthetic: json['is_synthetic'] ?? true,
      verificationHash: json['verification_hash'],
      safeAttributes: json['safe_attributes'] as Map<String, dynamic>?,
      privacyNotice: json['privacy_notice'],
    );
  }
}

