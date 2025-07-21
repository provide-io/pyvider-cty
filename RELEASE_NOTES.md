# Release Notes - v0.1.0-preview1

## 🎉 First Preview Release!

We're excited to announce the first preview release of pyvider.cty, a pure-Python implementation of the go-cty type system.

## ✨ Features

- **Complete Type System**: All go-cty types are implemented
- **Cross-Language Compatibility**: Interoperates with go-cty via JSON and MessagePack
- **Type Safety**: Strong validation ensures data integrity
- **Developer Friendly**: Pythonic API with clear error messages
- **Well Tested**: 920 tests with 84.6% code coverage

## 📦 What's Included

### Types
- Primitives: String, Number, Bool
- Collections: List, Set, Map
- Structural: Object, Tuple
- Special: Dynamic, Unknown, Null

### Features
- JSON serialization/deserialization
- MessagePack support (with known limitations)
- Path-based navigation for nested data
- Marks system for metadata
- Comprehensive error handling

## ⚠️ Known Limitations

1. **Python 3.13+ Required**: Due to modern type features
2. **MessagePack Compatibility**: Some edge cases with go-cty
3. **Performance**: Not yet optimized for large data structures
4. **Coverage**: Some error paths need more testing

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Migration from go-cty](docs/MIGRATION_FROM_GO_CTY.md)
- [API Documentation](docs/api/)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🔮 What's Next

- Improve test coverage to 95%+
- Performance optimization
- Additional serialization formats
- Enhanced error messages
- Community feedback integration

## 🙏 Thank You

Special thanks to the HashiCorp team for go-cty, which inspired this project.

## 📞 Get in Touch

- Issues: [GitHub Issues](https://github.com/provide/pyvider-cty/issues)
- Discussions: [GitHub Discussions](https://github.com/provide/pyvider-cty/discussions)
- Email: code@provide.io

Happy coding! 🐍✨
