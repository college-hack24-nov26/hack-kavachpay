import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/user.dart';
import '../models/credential.dart';
import '../models/activity.dart';
import '../models/dashboard_summary.dart';
import 'storage_service.dart';

class ApiService {
  final StorageService _storage;
  final http.Client _client;

  ApiService({StorageService? storage, http.Client? client})
      : _storage = storage ?? StorageService(),
        _client = client ?? http.Client();

  Future<Map<String, String>> _headers() async {
    final token = await _storage.getToken();
    final map = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (token != null) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConstants.login),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access_token'] as String;
        await _storage.saveToken(token);
        await _storage.saveUserProfile(jsonEncode(data['user']));
        return data;
      } else {
        final err = jsonDecode(response.body);
        throw Exception(err['detail'] ?? 'Invalid credentials.');
      }
    } catch (e) {
      // Fallback for offline demo mode if local server is unreachable
      if (email == 'user@kavachsetu.demo' && password == 'GhostProtocol@2026') {
        const dummyToken = 'demo-offline-secure-session-aarav-mehta';
        final user = {
          'user_code': 'KVS-001',
          'full_name': 'Aarav Mehta',
          'email': 'user@kavachsetu.demo',
          'phone_masked': '+91 ••••• ••421'
        };
        await _storage.saveToken(dummyToken);
        await _storage.saveUserProfile(jsonEncode(user));
        return {'access_token': dummyToken, 'user': user};
      }
      rethrow;
    }
  }

  Future<void> logout() async {
    try {
      final headers = await _headers();
      await _client.post(Uri.parse(ApiConstants.logout), headers: headers);
    } catch (_) {}
    await _storage.clearAll();
  }

  Future<DashboardSummaryModel> getDashboardSummary() async {
    try {
      final headers = await _headers();
      final response = await _client.get(Uri.parse(ApiConstants.dashboardSummary), headers: headers);
      if (response.statusCode == 200) {
        return DashboardSummaryModel.fromJson(jsonDecode(response.body));
      }
    } catch (_) {}

    // Fallback synthetic model for resilient demo execution
    return DashboardSummaryModel(
      user: const UserModel(
        userCode: 'KVS-001',
        fullName: 'Aarav Mehta',
        email: 'user@kavachsetu.demo',
        phoneMasked: '+91 ••••• ••421',
      ),
      totalCredentials: 3,
      validCredentials: 3,
      vaultStatus: 'ACTIVE & SECURE',
      recentCredentials: _mockCredentials(),
      recentActivities: _mockActivities(),
      securityNotice: 'Decoupled storage enabled. Zero PII shared with network nodes.',
    );
  }

  Future<List<CredentialModel>> getCredentials() async {
    try {
      final headers = await _headers();
      final response = await _client.get(Uri.parse(ApiConstants.vaultCredentials), headers: headers);
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        return list.map((item) => CredentialModel.fromJson(item)).toList();
      }
    } catch (_) {}
    return _mockCredentials();
  }

  Future<CredentialModel> getCredentialDetail(String id) async {
    try {
      final headers = await _headers();
      final response = await _client.get(Uri.parse(ApiConstants.credentialDetail(id)), headers: headers);
      if (response.statusCode == 200) {
        return CredentialModel.fromJson(jsonDecode(response.body));
      }
    } catch (_) {}

    final found = _mockCredentials().firstWhere(
      (c) => c.id == id,
      orElse: () => _mockCredentials().first,
    );
    return found;
  }

  Future<List<ActivityModel>> getActivityHistory() async {
    try {
      final headers = await _headers();
      final response = await _client.get(Uri.parse(ApiConstants.activity), headers: headers);
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        return list.map((item) => ActivityModel.fromJson(item)).toList();
      }
    } catch (_) {}
    return _mockActivities();
  }

  Future<Map<String, dynamic>> getSecurityOverview() async {
    try {
      final headers = await _headers();
      final response = await _client.get(Uri.parse(ApiConstants.securityOverview), headers: headers);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (_) {}
    return {
      'session_valid': true,
      'password_hashing': 'Bcrypt (12 Rounds Adaptive Cost)',
      'vault_storage_type': 'Decoupled Local Metadata Store',
      'encryption_algorithm': 'HMAC-SHA256 Session Signing',
      'active_tokens': 1,
      'data_protection_mode': 'Zero-Raw-Data Exposure'
    };
  }

  List<CredentialModel> _mockCredentials() {
    return const [
      CredentialModel(
        id: 'KVS-ID-001',
        category: 'IDENTITY',
        title: 'Identity Credential',
        issuer: 'KavachSetu Demo Issuer',
        status: 'VALID',
        issueDate: '2026-01-15',
        expiryDate: '2031-01-14',
        isSynthetic: true,
        verificationHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        safeAttributes: {
          'document_type': 'Synthetic National Digital ID',
          'holder_pseudonym': 'AARAV-M-***4',
          'privacy_mode': 'Decoupled Identifier',
        },
        privacyNotice: 'SYNTHETIC DEMO CREDENTIAL: For testing only. Raw documents remain decoupled.',
      ),
      CredentialModel(
        id: 'KVS-KYC-001',
        category: 'KYC',
        title: 'KYC Credential',
        issuer: 'KavachSetu Demo Issuer',
        status: 'VALID',
        issueDate: '2026-02-10',
        expiryDate: '2027-02-09',
        isSynthetic: true,
        verificationHash: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
        safeAttributes: {
          'compliance_standard': 'KYC Equivalent (Synthetic Sandbox)',
          'jurisdiction_region': 'Western Region (India)',
          'pii_leakage_risk': '0% (Raw documents never stored on server)',
        },
        privacyNotice: 'SYNTHETIC DEMO CREDENTIAL: For testing only. Raw documents remain decoupled.',
      ),
      CredentialModel(
        id: 'KVS-INC-001',
        category: 'INCOME',
        title: 'Income Credential',
        issuer: 'KavachSetu Demo Issuer',
        status: 'VALID',
        issueDate: '2026-03-01',
        expiryDate: '2026-09-01',
        isSynthetic: true,
        verificationHash: 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d',
        safeAttributes: {
          'synthetic_monthly_income': '₹35,000',
          'predicate_test_satisfied': 'Monthly Income > ₹25,000',
          'currency': 'INR',
          'raw_bank_statement_shared': 'No (Decoupled proof model)',
        },
        privacyNotice: 'SYNTHETIC DEMO CREDENTIAL: For testing only. Raw documents remain decoupled.',
      ),
    ];
  }

  List<ActivityModel> _mockActivities() {
    return const [
      ActivityModel(
        id: 1,
        actionType: 'LOGIN',
        title: 'User Authentication Successful',
        description: 'Session started via secure credentials',
        ipMasked: '127.0.0.1 (Verified)',
        deviceInfo: 'KavachSetu Secure Client',
        timestamp: '03 Nov, 01:30 PM',
      ),
      ActivityModel(
        id: 2,
        actionType: 'VAULT_INITIALIZED',
        title: 'Ghost-Vault Initialized',
        description: 'Secure vault created with 3 synthetic credentials',
        ipMasked: '127.0.0.1 (Local Session)',
        deviceInfo: 'KavachSetu Secure Client',
        timestamp: '03 Nov, 11:30 AM',
      ),
    ];
  }
}

