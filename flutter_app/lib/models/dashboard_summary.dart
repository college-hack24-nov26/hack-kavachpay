import 'user.dart';
import 'credential.dart';
import 'activity.dart';

class DashboardSummaryModel {
  final UserModel user;
  final int totalCredentials;
  final int validCredentials;
  final String vaultStatus;
  final List<CredentialModel> recentCredentials;
  final List<ActivityModel> recentActivities;
  final String securityNotice;

  const DashboardSummaryModel({
    required this.user,
    required this.totalCredentials,
    required this.validCredentials,
    required this.vaultStatus,
    required this.recentCredentials,
    required this.recentActivities,
    required this.securityNotice,
  });

  factory DashboardSummaryModel.fromJson(Map<String, dynamic> json) {
    return DashboardSummaryModel(
      user: UserModel.fromJson(json['user'] ?? {}),
      totalCredentials: json['total_credentials'] ?? 0,
      validCredentials: json['valid_credentials'] ?? 0,
      vaultStatus: json['vault_status'] ?? 'ACTIVE & SECURE',
      recentCredentials: (json['recent_credentials'] as List? ?? [])
          .map((item) => CredentialModel.fromJson(item))
          .toList(),
      recentActivities: (json['recent_activities'] as List? ?? [])
          .map((item) => ActivityModel.fromJson(item))
          .toList(),
      securityNotice: json['security_notice'] ?? '',
    );
  }
}

