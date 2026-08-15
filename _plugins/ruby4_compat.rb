# Liquid 4 still calls String#tainted?, which Ruby 4 removed.
class Object
  def tainted?
    false
  end unless method_defined?(:tainted?)
end
