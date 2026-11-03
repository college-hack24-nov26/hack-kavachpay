import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StorageService {
  final FlutterSecureStorage _storage;
  static const String _tokenKey = 'kavach_auth_token';
  static const String _userKey = 'kavach_user_profile';

  // In-memory fallback if platform secure storage is unavailable
  static String? _memToken;
  static String? _memUser;

  StorageService([FlutterSecureStorage? storage])
      : _storage = storage ?? const FlutterSecureStorage();

  Future<void> saveToken(String token) async {
    _memToken = token;
    try {
      await _storage.write(key: _tokenKey, value: token);
    } catch (_) {}
  }

  Future<String?> getToken() async {
    if (_memToken != null) return _memToken;
    try {
      final token = await _storage.read(key: _tokenKey);
      _memToken = token;
      return token;
    } catch (_) {
      return _memToken;
    }
  }

  Future<void> saveUserProfile(String userJson) async {
    _memUser = userJson;
    try {
      await _storage.write(key: _userKey, value: userJson);
    } catch (_) {}
  }

  Future<String?> getUserProfile() async {
    if (_memUser != null) return _memUser;
    try {
      final user = await _storage.read(key: _userKey);
      _memUser = user;
      return user;
    } catch (_) {
      return _memUser;
    }
  }

  Future<void> clearAll() async {
    _memToken = null;
    _memUser = null;
    try {
      await _storage.deleteAll();
    } catch (_) {}
  }
}

