# Maintainer: Scott Werner <scott.werner.vt@gmail.com>
pkgname=clipmanager
pkgver=master
pkgrel=1
pkgdesc="Python Qt GUI clipboard manager"
arch=('any')
url="https://github.com/scottwernervt/clipmanager"
license=('BSD')
depends=('python2' 'python2-setuptools' 'python2-pyside' 'python2-xlib')
optdepends=('xdotool: paste into active window')
install=$pkgname.install
changelog=CHANGELOG.rst
source=("https://github.com/scottwernervt/${pkgname}/archive/${pkgver}.tar.gz")
md5sums=('SKIP') #autofill using updpkgsums

package() {
  cd $pkgname-$pkgver

  python2 ./setup.py install --root="$pkgdir/"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}