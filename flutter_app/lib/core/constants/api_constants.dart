class ApiConstants {
  ApiConstants._();

  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';

  static const String login = '$baseUrl/auth/login';
  static const String logout = '$baseUrl/auth/logout';
  static const String me = '$baseUrl/auth/me';

  static const String vaultCredentials = '$baseUrl/vault/credentials';
  static String credentialDetail(String id) => '$baseUrl/vault/credentials/$id';

  static const String activity = '$baseUrl/activity';
  static const String dashboardSummary = '$baseUrl/dashboard/summary';
  static const String securityOverview = '$baseUrl/settings/security-overview';
}

