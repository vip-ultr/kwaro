# Homebrew formula for kwaro (tap: vip-ultr/homebrew-kwaro -> Formula/kwaro.rb)
#
# kwaro is a pure-Python, zero-runtime-dependency CLI, so this formula just builds
# the PyPI sdist. No native compilation, no per-OS bottles needed.
class Kwaro < Formula
  desc "Free, local security scanner: find, prove, fix, verify vulnerabilities"
  homepage "https://github.com/vip-ultr/kwaro"
  url "https://files.pythonhosted.org/packages/source/k/kwaro/kwaro-0.6.0.tar.gz"
  sha256 "cf09fbb3248f92960f56e02002951fd0835409a42c4e4c2174e8c4958a943d93"
  license "AGPL-3.0-only"
  head "https://github.com/vip-ultr/kwaro.git", branch: "master"

  depends_on "python@3.12"

  def install
    python3 = Formula["python@3.12"].opt_libexec/"bin/python"
    system python3, "-m", "pip", "install", "--prefix=#{prefix}", "."
  end

  test do
    assert_match "kwaro", shell_output("#{bin}/kwaro --help")
  end
end
