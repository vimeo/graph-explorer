
var App = angular.module('App', []);

App.controller('Ctrl', function($scope) {
    $scope.data = [[[0, 1], [1, 5], [2, 2]]];
});

App.directive('chart', function() {
    return {
        restrict: 'E',
        link: function(scope, elem, attrs) {
            var data = scope[attrs.ngModel];
            $.plot(elem, data, {});
            elem.show();
        }
    };
});
