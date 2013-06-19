# Maintainer: Scott Werner <scott.werner.vt@gmail.com>

pkgname=clipmanager
pkgver=0.3
pkgrel=0
pkgdesc="Manage the system's clipboard history."
url="https://bitbucket.org/mercnet/clipmanager"
arch=('any')
license=('BSD')
depends=('python2'
		 'python2-distribute'
		 'python2-pyside'
		 'python2-keybinder2'
		 'xdotool')
install=$pkgname.install
source=("https://bitbucket.org/mercnet/clipmanager/downloads/${pkgname}-${pkgver}.tar.gz")
md5sums=('49aab74e79bda06d0e4afd9c8379a303')

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python setup.py install --root="$pkgdir/" --optimize=1
}

# vim:set ts=2 sw=2 et: